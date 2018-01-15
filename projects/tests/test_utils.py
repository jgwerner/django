import os
import shutil
from unittest.mock import patch, mock_open
from pathlib import Path
from django.conf import settings
from django.test import TestCase
from users.models import User
from projects.models import ProjectFile, Project
from projects.utils import sync_project_files_from_disk, create_templates, read_project_files, create_project_files
from .utils import generate_random_file_content
from .factories import CollaboratorFactory, ProjectFileFactory


class ProjectUtilsTest(TestCase):
    def setUp(self):
        self.dirs_to_destroy = []

    def tearDown(self):
        for directory in self.dirs_to_destroy:
            shutil.rmtree(str(directory))

    # read_project_files
    @patch('os.walk')
    def test_read_project_files__root_files__return_root_files(self, mock_os_walk):
        proj = CollaboratorFactory().project
        test_file = "test_file_foo.txt"
        mock_os_walk.return_value = [(str(proj.resource_root()), [], [test_file])]
        files = read_project_files(str(proj.resource_root()))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], str(proj.resource_root()) + "/" + test_file)

    @patch('os.walk')
    def test_read_project_files__nested_files__return_nested_files(self, mock_os_walk):
        proj = CollaboratorFactory().project
        nested_path = "foo/bar/"
        test_file = "test_file_foo.txt"
        mock_os_walk.return_value = [(str(proj.resource_root()), ["foo"], []),
                                     (str(proj.resource_root()) + "/foo", ["bar"], []),
                                     (str(proj.resource_root()) + "/foo/bar", [], [test_file])]
        files = read_project_files(str(proj.resource_root()))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], str(proj.resource_root()) + "/" + nested_path + test_file)

    @patch('projects.utils.log')
    @patch('os.walk')
    def test_read_project_files__nfs_file__log_skipped_nfs_file(self, mock_os_walk, mock_logger):
        proj = CollaboratorFactory().project
        test_file = ".nfs_test_file_foo.txt"
        mock_os_walk.return_value = [(str(proj.resource_root()), [], [test_file])]
        files = read_project_files(str(proj.resource_root()))
        self.assertEqual(len(files), 0)
        mock_logger.info.assert_called_with("NFS system files found during sync process. Skipping them.")

    @patch('os.walk')
    def test_read_project_files__no_files__return_empty_list(self, mock_os_walk):
        proj = CollaboratorFactory().project
        mock_os_walk.return_value = [(str(proj.resource_root()), [], [])]
        files = read_project_files(str(proj.resource_root()))
        self.assertEqual(len(files), 0)
    # end read_project_files

    # create_project_files

    @patch('projects.utils.open', mock_open())
    @patch('projects.utils.File')
    @patch('projects.utils.log')
    def test_create_project_files__3_files__creates_3_project_files(self, mock_log, mock_file):
        proj = CollaboratorFactory().project
        paths_to_create = ["foo/bar/test1.txt", "foo/bar/test2.txt", "foo/bar/test3.txt"]
        mock_file.side_effect = paths_to_create
        create_project_files(proj, paths_to_create)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), len(paths_to_create))
        mock_log.info.assert_called_with(f"Created {len(paths_to_create)} ProjectFile objects in the database.")

    @patch('projects.utils.open', mock_open())
    @patch('projects.utils.File')
    @patch('projects.utils.log')
    def test_create_project_files__no_files__creates_0_project_files(self, mock_log, mock_file):
        proj = CollaboratorFactory().project
        paths_to_create = []
        mock_file.side_effect = paths_to_create
        create_project_files(proj, paths_to_create)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), len(paths_to_create))
        mock_log.info.assert_called_with(f"Created {len(paths_to_create)} ProjectFile objects in the database.")
    # end create_project_files

    def test_sync_project_files(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR))
        proj.resource_root().mkdir(parents=True)
        generate_random_file_content(suffix="foo.txt",
                                     base_path=str(proj.resource_root()))
        self.assertEqual(0, ProjectFile.objects.filter(project=proj).count())
        sync_project_files_from_disk(proj)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), 1)
        self.assertEqual(new_pf.first().file.name, str(proj.resource_root()).replace(settings.RESOURCE_DIR + "/", "") +
                         "/" + "test_file_foo.txt")

    def test_sync_files_nested_location(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR))
        proj.resource_root().mkdir(parents=True)
        Path(proj.resource_root(), "test_file_foo/bar/my/path").mkdir(parents=True)
        generate_random_file_content(suffix="foo/bar/my/path/fizz.txt",
                                     base_path=str(proj.resource_root()))
        self.assertEqual(0, ProjectFile.objects.filter(project=proj).count())
        sync_project_files_from_disk(proj)
        new_pf = ProjectFile.objects.filter(project=proj)
        self.assertEqual(new_pf.count(), 1)
        self.assertEqual(new_pf.first().file.name,
                         str(proj.resource_root()).replace(settings.RESOURCE_DIR + "/", "") +
                         "/" + "test_file_foo/bar/my/path/fizz.txt")

    def test_sync_files_delete(self):
        proj = CollaboratorFactory().project
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR))
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
        self.assertTrue(paths[0].replace(settings.RESOURCE_DIR + "/", "") not in file_names_list)
        self.assertTrue(paths[1].replace(settings.RESOURCE_DIR + "/", "") not in file_names_list)

    def test_create_templates(self):
        create_templates()
        user = User.objects.filter(username="3bladestemplates").first()
        self.assertIsNotNone(user)

        project = Project.objects.filter(name=settings.GETTING_STARTED_PROJECT).first()
        self.assertIsNotNone(project)

        proj_files = ProjectFile.objects.filter(project=project)
        self.assertEqual(proj_files.count(), 2)
        self.dirs_to_destroy.append(Path(settings.RESOURCE_DIR))
