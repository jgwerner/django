import shutil
import sqlite3
import logging
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.urls import reverse
from requests_oauthlib import OAuth1Session

from appdj.canvas.models import CanvasInstance
from appdj.servers.spawners import get_spawner_class

logger = logging.getLogger(__name__)


class Assignment:
    def __init__(self, path, aid=None, course_id=None, user_id=None, outcome_url=None, instance_guid=None, source_did=None):
        self.id = aid
        self.course_id = course_id
        self.user_id = user_id
        # relative path of assignment file ex. `dir/file.ipynb`
        self.path = Path(path).relative_to('release') if path.startswith('release') else Path(path)
        self.outcome_url = outcome_url
        self.instance_guid = instance_guid
        self.source_did = source_did

    def assign(self, teacher_project, student_project):
        """
        Copy assignment from teacher to student
        """
        source = self.teachers_path(teacher_project.resource_root()).parent
        destination = self.students_path(student_project.resource_root()).parent
        destination.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Copy assignment file from teachers path %s to students path %s", source, destination)
        shutil.copytree(source, destination)

    def submit(self, teacher_project, student_project):
        """
        Submit assignment
        """
        self.copy_submitted_file(teacher_project, student_project)

        self.autograde(teacher_project)

        grade = self.get_grade(teacher_project, student_project.owner)

        self.send(teacher_project, student_project.owner, grade)

    def to_dict(self):
        return {
            'aid': self.id,
            'course_id': self.course_id,
            'user_id': self.user_id,
            'path': str(self.path),
            'outcome_url': self.outcome_url,
            'instance_guid': self.instance_guid,
            'source_did': self.source_did
        }

    def teachers_path(self, teacher_project_root):
        """
        Describes where assignment file resides in teachers project
        We're using here nbgrader directory structure.
        """
        return teacher_project_root / 'release' / self.path

    def students_path(self, student_project_root):
        """
        Where student will find assignment file
        """
        return student_project_root / self.path

    def submission_path(self, teacher_project_root, student_username):
        """
        Where assignment file should be submitted
        """
        return teacher_project_root / 'submitted' / student_username / self.path

    def autograde(self, teacher_project):
        """
        Autograde assignment
        """
        Spawner = get_spawner_class()
        workspace = teacher_project.servers.first()
        spawner = Spawner(workspace)
        assignment_id = self.path.parent
        spawner.client.containers.run(
            settings.JUPYTER_IMAGE,
            f'nbgrader db assignment add {assignment_id}'
        )
        spawner.client.containers.run(
            settings.JUPYTER_IMAGE,
            f'nbgrader autograde "{assignment_id}" --create',
            volumes=spawner._get_binds()
        )

    def get_grade(self, teacher_project, student):
        """
        Retrieve grade from nbgrader gradebook.db file
        """
        course_db_path = teacher_project.resource_root() / 'gradebook.db'
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
                WHERE submitted_assignment.student_id = ?
            """,
            (student.username,)
        )
        grade = int(float(c.fetchone()[0]))
        logger.info("Student %s grade %s", student, grade)
        return grade

    def copy_submitted_file(self, teacher_project, student_project):
        """
        Copy student assignment file to teacher submitted directory
        """
        source = self.students_path(student_project.resource_root())
        destination = self.submission_path(teacher_project.resource_root(), student_project.get_owner_name())
        destination.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Submit assignment file from %s to %s", source, destination)
        shutil.copy(source, destination)

    def send(self, teacher_project, student, grade):
        """
        Send assiignment to canvas
        """
        canvas_apps = CanvasInstance.objects.get(
            instance_guid=self.instance_guid).applications.values_list('id', flat=True)
        teacher_workspace = teacher_project.servers.get(is_active=True, config__type='jupyter')
        oauth_app = student.profile.applications.filter(id__in=canvas_apps).first()
        oauth_session = OAuth1Session(oauth_app.client_id, client_secret=oauth_app.client_secret)
        scheme = 'https' if settings.HTTPS else 'http'
        namespace = teacher_project.namespace_name
        url_path = reverse('lti-file', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': namespace,
            'project_project': str(teacher_project.pk),
            'server': str(teacher_workspace.pk),
            'path': self.submission_path(teacher_project.resource_root(), student.username)
        })
        domain = Site.objects.get_current().domain
        url = f"{scheme}://{domain}{url_path}"
        logger.debug(f"[Send assignment] Server url: {url}")
        context = {
            'msg_id': uuid.uuid4().hex,
            'source_did': self.source_did,
            'url': url,
            'grade': grade
        }
        xml = render_to_string('servers/assignment.xml', context)
        response = oauth_session.post(self.outcome_url, data=xml,
                                      headers={'Content-Type': 'application/xml'})
        response.raise_for_status()


def create_canvas_assignment(data, path):
    return Assignment(
        aid=data['custom_canvas_assignment_id'],
        course_id=data['custom_canvas_course_id'],
        user_id=data['custom_canvas_user_id'],
        path=path,
        outcome_url=data['lis_outcome_service_url'],
        instance_guid=data['tool_consumer_instance_guid'],
        source_did=data.get('lis_result_sourcedid'),
    )
