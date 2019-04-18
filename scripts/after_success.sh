#!/bin/bash

set -e

docker_ecr_login () {
    eval $(aws ecr get-login --no-include-email)
}

# no need to build and tag images for pull requests.
tag_and_push () {
  if [ "${TRAVIS_PULL_REQUEST}" == "false" ]; then
    if [ "${TRAVIS_BRANCH}" == "${GITHUB_DEV_BRANCH}" ]; then
      export TAG="${GITHUB_DEV_BRANCH}"-"${TRAVIS_BUILD_NUMBER}"
      make build-all-proxies;
      make push-all-proxies;
      make build-app-backend;
      make push-app-backend;
      export TAG="${GITHUB_DEV_BRANCH}"-latest
      make build-all-proxies;
      make push-all-proxies;
      make build-app-backend;
      make push-app-backend;
    elif [ "${TRAVIS_BRANCH}" == "${GITHUB_PROD_BRANCH}" ]; then
      export TAG="${GITHUB_PROD_BRANCH}"-"${TRAVIS_BUILD_NUMBER}"
      make build-all-proxies;
      make push-all-proxies;
      make build-app-backend;
      make push-app-backend;
      export TAG="${GITHUB_PROD_BRANCH}"-latest
      make build-all-proxies;
      make push-all-proxies;
      make build-app-backend;
      make push-app-backend;
    fi
  fi
}

main () {
  echo "AWS ECR login..."
  docker_ecr_login
  echo "Build and push images..."
  tag_and_push
}

main