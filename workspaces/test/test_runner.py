import os
import unittest
 
from . import notebook_runner
 
 
class TestNotebook(unittest.TestCase):
 
    def test_runner(self):
        nb, errors = notebook_runner.run_notebook('test/test_notebook.ipynb')
        self.assertEqual(errors, [])
 
 
if __name__ == '__main__':
    unittest.main()