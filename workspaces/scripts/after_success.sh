
#!/bin/bash

set -e

change_directory () {
    cd $HOME/build/IllumiDesk/illumidesk/workspaces
}

docker_login () {
    eval $(aws ecr get-login --no-include-email --region ${AWS_REGION})
}

# no need to build and tag images for pull requests.
tag_and_push () {
  if [ "${TRAVIS_PULL_REQUEST}" == "false" ]; then
    if [ "${TRAVIS_BRANCH}" == "${GITHUB_DEV_BRANCH}" ]; then
      export TAG="${GITHUB_DEV_BRANCH}"-"${TRAVIS_BUILD_NUMBER}"
      make build-all;
      make push-all;
      make build-all TAG=latest;
      make push-all TAG=latest;
    elif [ "${TRAVIS_BRANCH}" == "${GITHUB_PROD_BRANCH}" ]; then
      export TAG="${GITHUB_PROD_BRANCH}"-"${TRAVIS_BUILD_NUMBER}"
      make build-all;
      make push-all;
      make build-all TAG=latest;
      make push-all TAG=latest;
    fi
  fi
}

main () {
  # linting errors shouldn't make travis fail
  set +e
  echo "Change into workspaces directory ..."
  change_directory
  echo "Log into DockerHub..."
  docker_login
  echo "Build and push images..."
  tag_and_push
}

main