import os
import shutil
from pathlib import Path
from django.conf import settings
from django.test import TestCase
from projects.models import ProjectFile
from projects.utils import sync_project_files_from_disk
from .utils import generate_random_file_content
from .factories import CollaboratorFactory, ProjectFileFactory


class ProjectUtilsTest(TestCase):
    def setUp(self):
        self.dirs_to_destroy = []

    def tearDown(self):
        for directory in self.dirs_to_destroy:
            shutil.rmtree(str(directory))

    def test_sync_project_files(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR, proj.owner.username))
        proj.resource_root().mkdir(parents=True)
        generate_random_file_content(suffix="foo.txt",
                                     base_path=str(proj.resource_root()))
        self.assertEqual(0, ProjectFile.objects.filter(project=proj).count())
        sync_project_files_from_disk(proj)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), 1)
        self.assertEqual(new_pf.first().file.name, str(proj.resource_root()) + "/" + "test_file_foo.txt")

    def test_sync_files_nested_location(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR, proj.owner.username))
        proj.resource_root().mkdir(parents=True)
        Path(proj.resource_root(), "test_file_foo/bar/my/path").mkdir(parents=True)
        generate_random_file_content(suffix="foo/bar/my/path/fizz.txt",
                                     base_path=str(proj.resource_root()))
        self.assertEqual(0, ProjectFile.objects.filter(project=proj).count())
        sync_project_files_from_disk(proj)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), 1)
        self.assertEqual(new_pf.first().file.name,
                         str(proj.resource_root()) + "/" + "test_file_foo/bar/my/path/fizz.txt")

    def test_sync_files_delete(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR, proj.owner.username))
        proj.resource_root().mkdir(parents=True)
        paths = []
        for x in range(4):
            uploaded_file = generate_random_file_content(f"{x}.txt")
            pf = ProjectFileFactory(author=proj.owner,
                                    project=proj,
                                    file=uploaded_file)
            paths.append(pf.file.path)

        for path in paths[:2]:
            os.remove(path)

        self.assertEqual(4, ProjectFile.objects.filter(project=proj).count())
        sync_project_files_from_disk(proj)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), 2)
        file_names_list = new_pf.values_list('file', flat=True)
        self.assertTrue(paths[0] not in file_names_list)
        self.assertTrue(paths[1] not in file_names_list)