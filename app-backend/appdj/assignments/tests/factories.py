import uuid
from pathlib import Path
import factory
from django.conf import settings

from appdj.canvas.tests.factories import CanvasInstanceFactory
from appdj.projects.tests.factories import ProjectFactory
from ..models import Assignment, Module, StudentProjectThrough


class AssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assignment

    external_id = factory.Sequence(lambda o: o)
    path = str(Path(settings.RESOURCE_DIR) / 'release/test/test.ipynb')
    outcome_url = 'https://outcome.example.com/'
    lms_instance = factory.SubFactory(CanvasInstanceFactory)
    teacher_project = factory.SubFactory(ProjectFactory)


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Module

    external_id = factory.Sequence(lambda o: o)
    path = str(Path(settings.RESOURCE_DIR) / 'release/test/test.ipynb')
    lms_instance = factory.SubFactory(CanvasInstanceFactory)
    teacher_project = factory.SubFactory(ProjectFactory)


class StudentProjectThroughFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProjectThrough

    assignment = factory.SubFactory(AssignmentFactory)
    project = factory.SubFactory(ProjectFactory)
    source_did = str(uuid.uuid4())
