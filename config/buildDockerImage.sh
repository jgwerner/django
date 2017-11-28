#!/bin/bash

if [ "$CIRCLE_PULL_REQUEST" == "" ]; then
  echo "Building docker image..."
  if [ "$CIRCLE_BRANCH" == "master" ]; then
   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
   docker build --no-cache -t $DOCKER_IMAGE_NAME .;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:build-$TRAVIS_BUILD_NUMBER;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:latest;
   docker push $DOCKER_IMAGE_NAME:build-$TRAVIS_BUILD_NUMBER;
   docker push $DOCKER_IMAGE_NAME:latest;
   # Auto Deploy To Rundeck dev-api.3blades.ai
   # echo "-- Starting Autodeploy dev-api deploy"
   #  curl https://maestro-staging.3blades.io/api/1/job/3b97a4d4-fdd2-40cb-bf3f-a24de0e23ccc/run?authtoken=$RUNDECK_KEY
   # echo "-- Done."a
  fi
  if [ "$CIRCLE_BRANCH" == "prod" ]; then
   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
   docker build --no-cache -t $DOCKER_IMAGE_NAME .;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:prod-build-$TRAVIS_BUILD_NUMBER;
   docker push $DOCKER_IMAGE_NAME:prod-build-$TRAVIS_BUILD_NUMBER;
   echo "-- Done."a
  fi
fi
