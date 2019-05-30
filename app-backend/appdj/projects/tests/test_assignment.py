from pathlib import Path
from unittest import TestCase

from appdj.projects.assignment import Assignment
from appdj.projects.tests.factories import CollaboratorFactory


class AssignmentTest(TestCase):
    def setUp(self):
        self.teacher_col = CollaboratorFactory()
        self.student_col = CollaboratorFactory()
        self.teacher_root = self.teacher_col.project.resource_root()
        self.teacher_root.mkdir(parents=True)
        self.student_root = self.student_col.project.resource_root()

    def test_assignment_init(self):
        path = 'release/test/test.ipynb'
        assignment = Assignment(
            path=path,
            aid=123,
            course_id=123,
            user_id=123,
            outcome_url='123',
            instance_guid=123,
            source_did=123
        )
        self.assertEqual(assignment.id, 123)
        self.assertEqual(assignment.path, Path(path))

    def test_assign(self):
        path = 'test/test.ipynb'
        assignment = Assignment(path=path)
        assignment.teachers_path(self.teacher_root).mkdir(parents=True)
        assignment.assign(self.teacher_col.project, self.student_col.project)
        self.assertTrue(assignment.students_path(self.student_root).exists())

    def test_submit(self):
        pass

    def test_teachers_path(self):
        assignment = Assignment('test/test.ipynb')
        out = str(assignment.teachers_path(self.teacher_root))
        self.assertIn(str(self.teacher_root), out)
        self.assertIn('release', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)

    def test_students_path(self):
        assignment = Assignment('test/test.ipynb')
        out = str(assignment.students_path(self.student_root))
        self.assertIn(str(self.student_root), out)
        self.assertNotIn('release', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)
        self.assertIn('test.ipynb', out)

    def test_submission_path(self):
        assignment = Assignment('test/test.ipynb')
        out = str(assignment.submission_path(self.teacher_root, self.student_col.user.username))
        self.assertIn(str(self.teacher_root), out)
        self.assertIn('submitted', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)
