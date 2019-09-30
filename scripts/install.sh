#!/bin/bash

set -e

copy_jupyter_lti_files () {
  mkdir workspaces/datascience-notebook/illumidesk_lti
  cp -r jupyter-lti/jupyterclassic/. workspaces/datascience-notebook/illumidesk_lti
}

create_env_file () {
  cp ./app-backend/env.compose ./app-backend/.env
}

create_docker_network () {
  make docker-network
}

create_rsa_keys () {
  openssl genrsa -out app-backend/rsa_private.pem 2048
  openssl rsa -in app-backend/rsa_private.pem -outform PEM -pubout -out app-backend/rsa_public.pem
}

make_build_backend () {
  make "TAG=dev" build-all-backends
}

make_build_proxies () {
  make "TAG=dev" build-all-proxies
}

install_aws_cli () {
  export PATH=$PATH:$HOME/.local/bin
  pip install awscli
}

install_terraform () {
  curl -fSL "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" -o terraform.zip
  sudo unzip terraform.zip -d /opt/terraform
  sudo ln -s /opt/terraform/terraform /usr/bin/terraform
  rm -f terraform.zip
}

main () {
  echo "Copy Jupyter nbextension files..."
  copy_jupyter_lti_files
  echo "Create .env file.."
  create_env_file
  echo "Creating docker network ${DOCKER_NETWORK}"
  create_docker_network
  echo "Create rsa keys ..."
  create_rsa_keys
  echo "Build images ..."
  make_build_backend
  make_build_proxies
  echo "Install aws cli ..."
  install_aws_cli
  echo "Install Terraform"
  install_terraform
}

main
