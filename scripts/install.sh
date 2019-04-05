#!/bin/bash

set -e

create_docker_network () {
  docker network create $DOCKER_NETWORK
}

docker_compose_build_dev () {
  docker-compose -f $DOCKER_COMPOSE_DEV build
}

make_build_proxies () {
  make "TAG=dev" build-all
}

install_aws_cli () {
  export PATH=$PATH:$HOME/.local/bin
  pip install awscli
}

install_ecs_deploy () {
  # lock it in to commit from Aug 8 2018
  curl https://raw.githubusercontent.com/silinternational/ecs-deploy/304051316ba576b1e0025c09a4a673f842885ba6/ecs-deploy | \
    sudo tee /usr/bin/ecs-deploy
  sudo chown travis:travis /usr/bin/ecs-deploy
  sudo chmod +x /usr/bin/ecs-deploy
}

main () {
  echo "Creating docker network ${DOCKER_NETWORK}"
  create_docker_network
  echo "Build images with docker-compose ..."
  docker_compose_build_dev
  make_build_proxies
  echo "Install aws cli ..."
  install_aws_cli
  echo "Install ecs-deploy ..."
  install_ecs_deploy
}

main
