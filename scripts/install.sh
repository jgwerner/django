#!/bin/bash

set -e

create_env_file () {
  cp ./app-backend/env.compose ./app-backend/.env
}

create_docker_network () {
  docker network create $DOCKER_NETWORK
}

docker_compose_build_dev () {
  docker-compose -f app-backend/$DOCKER_COMPOSE_DEV build
}

make_build_proxies () {
  make "TAG=dev" build-all-proxies
}

install_aws_cli () {
  export PATH=$PATH:$HOME/.local/bin
  pip install awscli
}

install_packer () {
  curl -fSL "https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_amd64.zip" -o packer.zip
  sudo unzip packer.zip -d /opt/packer
  sudo ln -s /opt/packer/packer /usr/bin/packer
  rm -f packer.zip
}

install_terraform () {
  curl -fSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o terraform.zip
  sudo unzip terraform.zip -d /opt/terraform
  sudo ln -s /opt/terraform/terraform /usr/bin/terraform
  rm -f terraform.zip
}

main () {
  echo "Create .env file.."
  create_env_file
  echo "Creating docker network ${DOCKER_NETWORK}"
  create_docker_network
  echo "Build images with docker-compose ..."
  docker_compose_build_dev
  make_build_proxies
  echo "Install aws cli ..."
  install_aws_cli
  echo "Install Terraform"
  install_terraform
}

main
