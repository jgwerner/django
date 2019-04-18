#!/bin/bash

set -e

# pylint w/ django plugin is run for reference lint score/messages.
run_linter () {
  echo "Running Pylint with Django plugin ..."
  docker-compose \
    -f ./app-backend/$DOCKER_COMPOSE_DEV \
    run \
    api ash -c "/srv/env/bin/pylint \
      --load-plugins pylint_django \
      appdj.base \
      appdj.canvas \
      appdj.infrastructure \
      appdj.jwt_auth \
      appdj.notifications \
      appdj.oauth2 \
      appdj.projects \
      appdj.search \
      appdj.servers \
      appdj.teams \
      appdj.users"
}

run_unit_tests () {
  docker-compose \
    -f app-backend/$DOCKER_COMPOSE_TEST \
    run beat ash -c \
    "/srv/env/bin/python manage.py test"
}

run_base_config_smoke_test () {
  docker-compose \
    -f app-backend/$DOCKER_COMPOSE_BASE \
    up -d
}

validate_exit_code_base_config () {
  # get container ID, get last runs exit code for each container ID, only non-0
  # status codes, count number of non-0 status codes, trim out white space
  cp ./app-backend/env.compose.dev ./app-backend/.env
  exit_status=$(docker-compose -f app-backend/$DOCKER_COMPOSE_BASE ps -q | xargs docker inspect \
    -f '{{ .State.ExitCode }}' | grep -v 0 | wc -l | tr -d ' ')
  if [[ ${exit_status} != 0 ]]; then
    echo "containers failed to start."; exit
  else
    # clean it up if exit 0
    docker-compose -f app-backend/$DOCKER_COMPOSE_BASE down
  fi
}

main () {
    # linting errors shouldn't make travis fail
    set +e
    echo "Running linter..."
    run_linter
    set -e
    echo "Running unit tests..."
    run_unit_tests
    echo "Validating config.base setup..."
    run_base_config_smoke_test
    validate_exit_code_base_config
}

main
