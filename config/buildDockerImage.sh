#!/bin/bash

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  export DOCKER_IMG_NUMBER=$((TRAVIS_BUILD_NUMBER + 950));
  if [ "$TRAVIS_BRANCH" == "master" ]; then
   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
   docker build --no-cache -t $DOCKER_IMAGE_NAME .;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:latest;
   docker push $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
   docker push $DOCKER_IMAGE_NAME:latest;
   # Auto Deploy To Rundeck dev-api.3blades.ai
   echo "-- Starting Autodeploy dev-api deploy"
    curl -d '{"buildType":{"id": "IllumiDesk_Deploy"}}' -H "Content-Type: application/json" -u "$TEAMCITY_USER":"$TEAMCITY_PASSWORD" -X POST "$TEAMCITY_URL/httpAuth/app/rest/buildQueue"
   echo "-- Done."a
  fi
  if [ "$TRAVIS_BRANCH" == "prod" ]; then
   docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
   docker build --no-cache -t $DOCKER_IMAGE_NAME .;
   docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:prod-build-$TRAVIS_BUILD_NUMBER;
   docker push $DOCKER_IMAGE_NAME:prod-build-$TRAVIS_BUILD_NUMBER;
   echo "-- Done."a
  fi
fi
