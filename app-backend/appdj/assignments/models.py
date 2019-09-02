import shutil
import uuid
import sqlite3
import logging
from pathlib import Path

from django.db import models
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.urls import reverse
from requests_oauthlib import OAuth1Session
from nbgrader.apps import NbGraderAPI
from nbgrader.coursedir import CourseDirectory
from traitlets.config import Config

from appdj.base.models import TBSQuerySet
from appdj.projects.models import Project

logger = logging.getLogger(__name__)


class StudentProjectThrough(models.Model):
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    source_did = models.TextField(blank=True)


class ModuleAbstract(models.Model):
    NATURAL_KEY = 'external_id'

    external_id = models.TextField()
    path = models.TextField()
    course_id = models.TextField(blank=True)

    objects = TBSQuerySet.as_manager()

    class Meta:
        abstract = True


class Assignment(ModuleAbstract):
    outcome_url = models.URLField(max_length=255, blank=True)
    lms_instance = models.ForeignKey(
        'canvas.CanvasInstance',
        related_name='assignments',
        on_delete=models.CASCADE
    )
    teacher_project = models.ForeignKey(
        'projects.Project',
        related_name='teacher_assignments',
        on_delete=models.CASCADE
    )
    students_projects = models.ManyToManyField(
        'projects.Project',
        related_name='student_assignments',
        through=StudentProjectThrough,
    )
    oauth_app = models.ForeignKey(
        'oauth2.Application',
        related_name='assignments',
        on_delete=models.SET_NULL, null=True
    )

    def students_path(self, student_project):
        """
        Where student will find assignment file
        """
        path = Path(self.path).relative_to('release') if 'release' in self.path else self.path
        return student_project.resource_root() / path

    @property
    def teachers_path(self):
        return self.teacher_project.resource_root() / self.path

    @property
    def assignment_id(self):
        return Path(self.path).parent.name

    @property
    def should_autograde(self):
        return b'nbgrader' in self.teachers_path.read_bytes()

    def assign(self, student_project):
        """
        Copy assignment from teacher to student
        """
        source = self.teachers_path.parent
        destination = self.students_path(student_project).parent
        is_student_root = destination == student_project.resource_root()
        if not is_student_root and not destination.is_dir():
            destination.mkdir(parents=True)
        if destination.exists() and not is_student_root:
            shutil.rmtree(destination)
            logger.info("Copy assignment file from teachers path %s to students path %s", source, destination)
            shutil.copytree(source, destination)
        else:
            shutil.copy2(self.teachers_path, destination)

    def is_assigned(self, student_project):
        """
        States if assignment file was copied to student directory
        """
        return self.students_path(student_project).exists()

    def submission_path(self, student_project):
        """
        Where assignment file should be submitted
        """
        student_username = student_project.owner.username
        path = Path(self.path).relative_to('release') if 'release' in self.path else self.path
        return self.teacher_project.resource_root() / 'submitted' / student_username / path

    def autograde(self, student_project):
        """
        Autograde assignment
        """
        config = Config()
        config.CourseDirectory.root = str(self.teacher_project.resource_root())
        api = NbGraderAPI(CourseDirectory(config=config), config=config)
        resp = api.autograde(self.assignment_id, student_project.owner.username, force=False)
        if not resp['success']:
            raise Exception(f"Assignment {self.external_id} not autograded for student {student_project.owner.username}: {resp}")

    def get_grade(self, student_project):
        """
        Retrieve grade from nbgrader gradebook.db file
        """
        course_db_path = self.teacher_project.resource_root() / 'gradebook.db'
        conn = sqlite3.connect(str(course_db_path))
        c = conn.cursor()
        c.execute(
            """
            SELECT SUM(grade.auto_score) as score
                FROM grade
                JOIN submitted_notebook
                    ON grade.notebook_id = submitted_notebook.id
                JOIN submitted_assignment
                    ON submitted_notebook.assignment_id = submitted_assignment.id
                JOIN assignment
                    ON submitted_assignment.assignment_id = assignment.id
                WHERE submitted_assignment.student_id = ? AND assignment.name = ?
            """,
            (student_project.owner.username, self.assignment_id)
        )
        grade = int(float(c.fetchone()[0]))
        logger.info("Student %s grade %s", student_project.owner, grade)
        return grade

    def copy_submitted_file(self, student_project):
        """
        Copy student assignment file to teacher submitted directory
        """
        source = self.students_path(student_project)
        destination = self.submission_path(student_project)
        destination.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Submit assignment file from %s to %s", source, destination)
        shutil.copy(source, destination)

    def send(self, student_project):
        """
        Send assiignment to canvas
        """
        self.copy_submitted_file(student_project)
        if self.should_autograde:
            self.autograde(student_project)
            grade = self.get_grade(student_project)
        teacher_workspace = self.teacher_project.servers.get(is_active=True, config__type='jupyter')
        oauth_session = OAuth1Session(
            self.oauth_app.application.client_id,
            client_secret=self.oauth_app.application.client_secret
        )
        scheme = 'https' if settings.HTTPS else 'http'
        namespace = self.teacher_project.namespace_name
        url_path = reverse('lti-file', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': namespace,
            'project_project': str(self.teacher_project.pk),
            'server': str(teacher_workspace.pk),
            'path': self.submission_path(student_project).relative_to(self.teacher_project.resource_root())
        })
        domain = Site.objects.get_current().domain
        url = f"{scheme}://{domain}{url_path}"
        logger.debug(f"[Send assignment] Server url: {url}")
        source_did = StudentProjectThrough.objects.get(assignment=self, project=student_project).source_did
        context = {
            'msg_id': uuid.uuid4().hex,
            'source_did': source_did,
            'url': url,
        }
        if self.should_autograde:
            context.update({
                'grade': grade
            })
        xml = render_to_string('servers/assignment.xml', context)
        response = oauth_session.post(self.outcome_url, data=xml,
                                      headers={'Content-Type': 'application/xml'})
        response.raise_for_status()


class Module(ModuleAbstract):
    lms_instance = models.ForeignKey(
        'canvas.CanvasInstance',
        related_name='modules',
        on_delete=models.CASCADE
    )
    teacher_project = models.ForeignKey(
        'projects.Project',
        related_name='teacher_modules',
        on_delete=models.CASCADE
    )
    students_projects = models.ManyToManyField(
        'projects.Project',
        related_name='student_modules'
    )
    oauth_app = models.ForeignKey(
        'oauth2.Application',
        related_name='modules',
        on_delete=models.SET_NULL, null=True
    )


def get_assignment_or_module(*, project_pk, course_id, user, path, assignment_id):
    cls = Assignment if assignment_id else Module
    qs = cls.objects.filter(
        teacher_project_id=project_pk,
        teacher_project__is_active=True,
        course_id=course_id,
        path=path
    )
    if assignment_id:
        qs = qs.filter(external_id=assignment_id)
    teacher_obj = qs.filter(
        teacher_project__collaborator__user=user,
        teacher_project__collaborator__owner=True,
    ).first()
    if teacher_obj is not None:
        return teacher_obj, True
    student_obj = qs.filter(
        students_projects__is_active=True,
        students_projects__collaborator__user=user,
        students_projects__collaborator__owner=True,
    ).first()
    return student_obj, False
