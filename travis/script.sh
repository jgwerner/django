set -e

if [ "$TEST_SUITE" = "UNIT" ]
then
    python -W ignore tbs_coverage.py run manage.py test --parallel 16 && coverage combine && coverage report -m
elif [ "$TEST_SUITE" = "API" ]
then
    docker-compose -f docker-compose-test.yml up --abort-on-container-exit
    docker logs appbackend_test_1
fi