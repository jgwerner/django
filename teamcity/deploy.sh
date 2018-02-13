#!/bin/bash
###
###
###
###   Purpose:      Tag and push app-backend as build number and latest. Authentication is handled in teamcity.
###   Author:       Josh Starrett (jstarrett@3blades.io)
###
### ######################################### ###

docker build --no-cache -t $DOCKER_IMAGE_NAME .;
docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
docker tag $DOCKER_IMAGE_NAME $DOCKER_IMAGE_NAME:latest;
docker push $DOCKER_IMAGE_NAME:build-$DOCKER_IMG_NUMBER;
docker push $DOCKER_IMAGE_NAME:latest;
