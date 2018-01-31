#!/bin/bash
###
###
###
###   Purpose:      Run unit tests inside teamcity build.
###   Author:       Josh Starrett (jstarrett@3blades.io)
###
### ######################################### ###

# Cleanup docker containers and cleanup directories
cleanup(){
    docker stop test-postgres
    docker rm test-postgres
    docker stop test-redis
    docker rm test-redis
    
    rm -rf /workspaces/
    rm -rf /tmp/3blades/
}
trap cleanup EXIT
# Startup test dependencies in containers
docker run --name test-postgres -p 5432:5432 -d postgres
docker run --name test-redis -p 6379:6379 -d redis
docker ps
# Install python package dependencies
python3.6 -m pip install -U pip setuptools wheel
python3.6 -m pip install -r requirements/dev.txt
python3.6 -m pip install codecov
python3.6 -m pip install teamcity-messages
# Setup teamcity test runner so we can test results in teamcity
echo 'TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"' >> appdj/settings/test.py
# Run the tests
python3.6 -W ignore tbs_coverage.py run manage.py test --parallel 16 && coverage combine && coverage report -m