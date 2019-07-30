[![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?token=y3jvxynhJQZHELnDYJdy&branch=master)](https://travis-ci.com/IllumiDesk/illumidesk)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

# IllumiDesk Backend Services

## Dev Setup with Docker

### Requirements

- [Python 3.6](https://www.python.org/downloads/release/python-360/)
- [Docker](https://docs.docker.com/engine/installation/)
- [Docker Compose](https://docs.docker.com/compose/install/)

> `docker-compose` may hang after installation. Apply executable permissions to docker-compose binary:

    sudo chmod +x /usr/local/bin/docker-compose

We maintain `docker-compose-*.yml` files to launch our working `app-backend` stack. Launching the full stack may be necessary to support integration testing, such as creating new user workspaces. Services include (in alphabetical order):

- [API](./app-backend): RESTful API based on Django and Django Rest Framework (DRF)
- [Postgres](https://hub.docker.com/_/postgres/)
- [Redis](https://hub.docker.com/_/redis/)
- [Traefik](https://hub.docker.com/_/traefik)
- [Nginx](https://hub.docker.com/_/nginx)

### Launch Stack

Establish your environment variables. The `env.compose.*` file included in this repo includes a sensible set of defaults which should work to launch a basic version of the application:

    cp env.compose.* .env

Use the following command to launch the full stack with docker compose (-d for detached mode):

    docker-compose -f docker-compose-dev.yml up -d

> `docker-compose-*.yml` mounts files from the host to allow for updating files on the host and having those reflected in the container's file system. `docker-compose-test.yml` builds images with `Dockerfile.Test` and is used to run integration and unit tests.

Create admin (superuser) user:

    docker-compose exec api /srv/env/bin/python manage.py createsuperuser

Collect static files:

    docker-compose exec api /srv/env/bin/python manage.py collectstatic

Access API docs page and login:

    http://localhost:5000/tbs-admin/

### Relaunch Stack After Code Update

Code updates are frequent and may require you to re launch stack. Use the development version of `docker-compose` to mount files from the host to the container. The development version has debugging enabled with the `DEBUG=True` environment variable. Code updates will trigger the Django server to reload files and settings into memory.

Sometimes its necessary to restart all docker-compose managed services like so:

    docker-compose -f docker-compose-dev.yml restart

If you remove all containders with `docker-compose down` or `docker rm -f $(docker ps -a -q)`, then
you will need to recreate your super user and fetch static assets:

    docker-compose up -f docker-compose-dev.yml -d
    docker-compose exec api /srv/env/bin/python manage.py collectstatic
    docker-compose exec api /srv/env/bin/python manage.py createsuperuser

### Run Tests

Update Django settings so that it uses `test` module:

    export DJANGO_SETTINGS_MODULE=config.settings.test

Run tests:

    docker-compose -f docker-compose-test.yml up -d
    docker-compose exec api /srv/env/bin/python manage.py test

## Dev Setup with Django on Host

Sometimes you may not need to run and test the full stack. Under these circumstances some developers may find that running the Django backend server directly on the host improves development/test cycles.

At a minimum, `app-backend` requires Postgres, Redis, and RabbitMQ.

To run services individually, use the docker run command.

Postgres:

    docker run --name my-postgres -p 5432:5432 -d postgres:10.4-alpine

Redis:

    docker run --name my-redis -p 6379:6379 -d redis:apline

RabbitMQ:

    docker run --name my-redis -d rabbitmq:alpine

Confirm environment variables:

    cp env.virtualenv .env

Set up virtualenv and install dependencies:

    virtualenv -p python3.6 venv
    source/venv/bin/activate
    pip install -r requirements/dev.txt

Run database migrations:

    python manage.py migrate

Create admin (superuser) user:

    python manage.py createsuperuser

Run application:

    python manage.py runserver 0.0.0.0:8000

Login:

    http://localhost:8000/tbs-admin/

> Note that the port when using `docker-compose` is `5000` and when using the virtual environment on the host it's `8000`.

### Run Tests

Update Django settings so that it uses `test` module:

    export DJANGO_SETTINGS_MODULE=config.settings.test

Run tests:

    python manage.py test

### Environment Variables

The IllumiDesk `app-backend` application interacts with various internal applications and external, third-party services. A list of the environment variables used by the IllumiDesk application [are located here](docs/ENV_VARIABLE_EXPLANATION.md).

## Trouble Shooting

### Environment variables

If you are running app-backend without docker, then you need to make sure all environment variables are set correctly. Verify by checking them with the echo command, such as:

    echo $DATABASE_HOST

Or, just print all of them with `printenv`.

## Contributing

### General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind
and build a nice open source community with us.

### Commit Messages

This projet adhere's to the [Conventional Commits](https://conventionalcommits.org) standard.

Changelogs are automated with [Standard Version](https://github.com/conventional-changelog/standard-version). Use the release command to
update the release and the changelog:

    npm run release

## Copyright and license

Copyright © 2019 IllumiDesk. All rights reserved, except as follows. Code
is released under the BSD 3.0 license. The README.md file, and files in the
"docs" folder are licensed under the Creative Commons Attribution 4.0
International License under the terms and conditions set forth in the file
"LICENSE.docs". You may obtain a duplicate copy of the same license, titled
CC-BY-SA-4.0, at http://creativecommons.org/licenses/by/4.0/.
