#!/bin/bash
###
###
###
###   Purpose:      Run api tests inside teamcity build.
###   Author:       Josh Starrett (jstarrett@3blades.io)
###
### ######################################### ###

set -e
# Cleanup all test data
finish(){
    docker logs appbackend_test_1
    docker-compose -f docker-compose-test.yml stop
    docker-compose -f docker-compose-test.yml rm --force
}
trap finish EXIT
# Start up container stack and exit when tests complete
docker-compose -f docker-compose-test.yml -p appbackend up --build --abort-on-container-exit