#!/bin/bash


docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD";
docker build --no-cache -t $DOCKER_IMAGE_NAME .;
docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:latest;
docker push $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
docker push $DOCKER_IMAGE_NAME:latest;
