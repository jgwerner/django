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

The IllumiDesk `app-backend` application interacts with various internal applications and external, third-party services. The following descriptions should help to understand the most important of these variables:

| Variable  |  Type | Note  |
|---|---|---|
| AWS_SES_ACCESS_KEY_ID |<string> | Pair with AWS_SES_SECRET_ACCESS_KEY to access Simple Email Service (SES) |
| AWS_SES_SECRET_ACCESS_KEY | <string> | Pair with AWS_SES_ACCESS_KEY_ID to access Simple Email Service (SES) |
| AWS_SES_REGION_NAME | <string> | Name of AWS SES region, a geographic area containing Amazon data centers |
| AWS_SES_REGION_ENDPOINT | <string> | API endpoint associated with AWS_SES_REGION_NAME |
| AWS_ACCESS_KEY_ID | <string> | User account ID key to access general Amazon Web Services (AWS) |
| AWS_SECRET_ACCESS_KEY | <string> | Secret key associated with AWS_ACCESS_KEY_ID |
| AWS_DEFAULT_REGION | <string> | Default region for AWS access |
| ECS_CLUSTER | <string> | Name of Elastic Container Service (ECS) Cluster |
| AWS_STORAGE_BUCKET_NAME | <string> | Your AWS storage bucket name |
| AWS_S3_CUSTOM_DOMAIN | <string> | Domain of S3, if used as a Content Delivery Network (CDN) |
| DATABASE_HOST=localhost | <string> | Database host |
| DATABASE_USER=postgres | <string> | Database user |
| DATABASE_PASSWORD | <string> | Database password |
| DATABASE_PORT | <string> | Database port |
| DATABASE_NAME | <string> | Database name |
| DEBUG | <boolean> | Enables the app's debug mode |
| DEFAULT_FROM_EMAIL | <email> | Default email address for sending app-backend messages |
| DEFAULT_STRIPE_PLAN_ID | <string> | Name of Stripe subscription plan (also the default for new users) |
| DJANGO_SETTINGS_MODULE | <string> | Module name of Django application settings file |
| DOCKER_DOMAIN | <string> | IP address of your Docker's domain |
| DOCKER_HOST | <string> | TCP address of your Docker's host |
| DOCKER_EVENTS_URL | <string> | URL for your Docker's events distributor |
| DOCKER_NET | <string> | Name of Docker Net |
| ELASTICSEARCH_URL | <string> | URL for Elasticsearch endpoint |
| ELASTICSEARCH_USER | <string> | Elasticsearch username |
| ELASTICSEARCH_PASSWORD | <string> | Password associated with ELASTICSEARCH_USER |
| EMAIL_HOST | <string> | Host address for email client |
| EMAIL_PORT | <integer> | Port number for email client |
| EMAIL_HOST_USER | <string> | Email host username |
| EMAIL_HOST_PASSWORD | <string> | Password associated with EMAIL_HOST_USER |
| EMAIL_USE_TLS | <boolean> | Enables Transport Layer Security (TLS) when talking to SMTP server |
| EMAIL_USE_SSL | <boolean> | Enables implicit TLS (commonly known as "SSL") when talking to SMTP server |
| EXTERNAL_IPV4 | <string> | External facing IPV4 address, required by webapp to accept connections without a domain name. |
| GITHUB_CLIENT_ID | <string> | Client ID for Github account |
| GITHUB_CLIENT_SECRET | <string> | Secret access key associated with GITHUB_CLIENT_ID |
| GOOGLE_CLIENT_ID | <string> | Client ID for Google account |
| GOOGLE_CLIENT_SECRET | <string> | Secret access key associated with GOOGLE_CLIENT_ID |
| MOCK_STRIPE | <boolean> | Enables use of mock connections to Stripe for development purposes |
| NVIDIA_DOCKER_HOST | <string> | URL for NVIDIA Docker host |
| RABBITMQ_URL | <string> | URL for RabbitMQ message broker |
| REDIS_URL | <string> | URL for Redis data store/notifications |
| RESOURCE_DIR | <string> | Root level directory for all user directories |
| SECRET_KEY | <string> | Secret key used for Django-related security |
| SENTRY_DSN | <string> | Data Source Name (DSN) for Sentry's error tracking and monitoring service |
| SERVER_PORT | <integer> | Port number for main application environment |
| SERVER_RESOURCE_DIR | <string> | Name of relevant project's resource directory. It should be notebooks workdir.|
| SLACK_KEY | <string> | Slack account ID key |
| SLACK_SECRET | <string> | Secret access key associated with SLACK_KEY |
| STATIC_ROOT | <string> | Absolute path to the directory static files should be collected to. |
| STRIPE_SECRET_KEY | <string> | Secret key associated with Stripe payment information |
| APP_DOMAIN | <string> | Domain of IllumiDesk main development environment |
| APP_SCHEME | <string> | An additional host name or IP address from which the application will allow connections, added to Django's ALLOWED_HOSTS |
| TLS | <boolean> | Enables application's use of secure HTTP |
| TRAVIS_PULL_REQUEST | <boolean> | Enables Travis CI's automated Docker image building upon pull request submission |

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
