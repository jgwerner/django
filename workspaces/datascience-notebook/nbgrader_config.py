# https://nbgrader.readthedocs.io/en/stable/configuration/config_options.html

c = get_config()

c.Application.log_level = 10
c.JupyterApp.config_file = '/etc/jupyter/jupyter_notebook_config.py'
c.CourseDirectory.directory_structure = '{nbgrader_step}/{student_id}/{assignment_id}'
c.CourseDirectory.feedback_directory = 'feedback'
c.CourseDirectory.autograded_directory = 'autograded'
c.CourseDirectory.release_directory = 'release'
c.CourseDirectory.source_directory = 'source'
c.CourseDirectory.submitted_directory = 'submitted'
c.Exchange.root = '/srv/nbgrader/exchange'