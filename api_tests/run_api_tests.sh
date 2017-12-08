#!/bin/bash
# run_api_tests.sh
set -e

function finish {
    docker-compose stop
}
trap finish EXIT

# read env variables
TEST_USER=AutoTester
TEST_USER_EMAIL=AutoTester@domain.com
TEST_USER_PASSWORD=Aut0123!
HOST=http://api
PORT=80

docker-compose -f docker-compose.test.yml up -d

docker build --file Dockerfile.Test -t api_tests .


docker run --rm -l api -e TEST_USER_EMAIL=$TEST_USER_EMAIL -e TEST_USER_PASSWORD=$TEST_USER_PASSWORD -e TEST_USER=$TEST_USER -e HOST=$HOST -e PORT=$PORT api_tests