#!/bin/bash

if [ "$TRAVIS_PULL_REQUEST" == "false" ] && [ "$TRAVIS_BRANCH" == "master" ]; then
   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
   docker build --no-cache -t $DOCKER_IMAGE_NAME .;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:build-$TRAVIS_BUILD_NUMBER;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:latest;
   docker push $DOCKER_IMAGE_NAME:build-$TRAVIS_BUILD_NUMBER;
   docker push $DOCKER_IMAGE_NAME:latest;
   # Auto Deploy To Rundeck
   curl https://maestro-staging.3blades.io/api/14/project/3blades_legacy/jobs?authtoken=$RUNDECK_NONPROD_API_KEY
fi
