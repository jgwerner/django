if [ "$TEST" = "UNIT" ]
then
    python -W ignore tbs_coverage.py run manage.py test --parallel 16 
    coverage combine && coverage report -m
else
    docker-compose -f docker-compose.test.yml up --abort-on-container-exit
fi