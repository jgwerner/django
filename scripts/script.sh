#!/bin/bash

set -e

# pylint w/ django plugin is run for reference lint score/messages.
run_linter () {
  echo "Running Pylint with Django plugin ..."
  docker-compose \
    -f ./app-backend/$DOCKER_COMPOSE_TEST \
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
  run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test \
  beat /srv/env/bin/python manage.py test
}

main () {
    # linting errors shouldn't make travis fail
    set +e
    echo "Running linter..."
    run_linter
    set -e
    echo "Running unit tests..."
    run_unit_tests
}

main
