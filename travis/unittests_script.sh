python -W ignore tbs_coverage.py run manage.py test --parallel 16 
coverage combine && coverage report -m