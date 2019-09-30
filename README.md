[![Build Status](https://travis-ci.com/IllumiDesk/illumidesk.svg?token=y3jvxynhJQZHELnDYJdy&branch=master)](https://travis-ci.com/IllumiDesk/illumidesk)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

# IllumiDesk Backend Services

## Setup

### Requirements

- [Python 3.6](https://www.python.org/downloads/release/python-360/)
- [Docker](https://docs.docker.com/engine/installation/)
- [Docker Compose](https://docs.docker.com/compose/install/)

> `docker-compose` may hang after installation. Apply executable permissions to docker-compose binary:

    sudo chmod +x /usr/local/bin/docker-compose

We maintain a `docker-compose.yml` files to launch our stack. Launching the full stack may be necessary to support integration testing, such as creating new user workspaces. Services include (in alphabetical order):

- [API](./app-backend): RESTful API based on Django and Django Rest Framework (DRF)
- [Postgres](https://hub.docker.com/_/postgres/)
- [Redis](https://hub.docker.com/_/redis/)
- [Traefik](https://hub.docker.com/_/traefik)
- [Nginx](https://hub.docker.com/_/nginx)

### Create RSA key pair

Create RSA key pair like so:

    cd app-backend
    openssl genpkey -algorithm RSA -out rsa_private.pem -pkeyopt rsa_keygen_bits:2048
    openssl rsa -in rsa_private.pem -pubout -out rsa_public.pem

### Docker and ECS Spawners

By default the config uses the `DockerSpawner` client to launch workspaces. Development, staging and production configuration should use the `ECSSpawner` client to launch workspaces with an AWS ECS cluster.

The `DOCKER_HOST` environment variable uses the unix socket to communicate with the docker daemon. If you wish to use a TCP based socket, refer to the Docker docs as this setup only considers the use of the `ECSSpawner` for installations that have workspaces on separate instances.

### Configuration Settings

The `DJANGO_SETTINGS_MODULE` provides a sensible set of defaults for different enviroments:

- Configuration for local development: `config.settings.local`
- Configuration with AWS ECS: `config.settings.dev`
- Configuration for tests: `config.settings.test`
- Configuration for production: `config.settings.prod`

## Launch Stack

Establish your environment variables. The `app-backend/env.compose` file included in this repo includes a sensible set of defaults which should work to launch a basic version of the application:

    cp app-backend/env.compose app-backend/.env

Use the following command to launch the full stack with `make`:

    cd app-backend
    docker-compose up -d

> `docker-compose.yml` mounts files using docker volumes. To persist data to a `/workspaces` directory located on the host, update the `docker-compose.yml` from `workspaces` to `/workspaces`.

Create admin (superuser) user:

    docker-compose exec api /srv/env/bin/python manage.py createsuperuser

Collect static files:

    docker-compose exec api /srv/env/bin/python manage.py collectstatic

Access API docs page and login:

    http://localhost:8001/tbs-admin/

### Relaunch Stack After Code Update

Code updates are frequent and may require you to re launch stack. Dev and production versions do not mount files from the host to obtain the source files. After code updates in a dev environment update them with:

    docker-compose down
    docker-compose build
    docker-compose up -d

Sometimes its necessary to restart all docker-compose managed services like so:

    docker-compose restart

> By default, `docker-compose down` removes volume containers, in which case you need to re create the super user and collect static files. If you are using `docker-compose` with AWS services, such as `AWS RDS`, then you can either comment out the db/cache containers before launching the stack or use `docker-compose down --remove-orphans` to remove orphaned containers.

### Destroy

Clean up all containers with:

    make destroy

This command will remove all containers (running and exited), volumes, and networks from the host.

### Run Tests

Set the the Django settings module environment variable to run unit and integration tests:

    docker-compose \
      run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test \
      beat /srv/env/bin/python manage.py test

Use the following command to run `lint` tests:

    docker-compose \
      run \
      -e DJANGO_SETTINGS_MODULE=config.settings.test \
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

> You can choose to run linting tests for one or all Django apps.

### Environment Variables

The IllumiDesk `app-backend` application interacts with various internal applications and external, third-party services. Please refer to the [environment variables document](./app-backend/docs/ENVIRONMENT_VARIABLES.md) for further reference.

> By default, the `env.compose` file sets `DJANGO_SETTINGS_MODULE

## Contributing

### General Guidelines

This project enforces the [Contributor Covenant](./CODE_OF_CONDUCT.md). Be kind and build a nice open source community with us.

### Commit Messages, Changelog, and Releases

This project uses Semantic Versioning with Conventional Commits to track major, minor, and patch releases. The `make release` command automates [CHANGLOG.md](./CHANGELOG.md) updates and release version metadata.

Once a new version is released, assets should be published with the new tag, such as docker images, npm packages, and GitHub repo release tags.

When stashing and merging to the `master` branch, use the following format to provide consistent updates to the `CHANGELOG.md` file:

    <Commit Type>(scope): <Merge Description>

- `Merge Description` should initiate with a capital letter, as it provides the changelog with a standard sentence structure.

- `Scope` is used to define what is being updated. Our current scopes include:

1. core
2. frontend
3. workspace
4. grader

- `Commit Types` are listed below:

| Commit Type | Commit Format |
| --- | --- |
| Chores | `chore` |
| Docs | `docs` |
| Features | `feat` |
| Fixes | `fix` |
| Performance | `perf` |
| Refactoring | `refactor` |

Use the `BREAKING CHANGE` in the commit's footer if a release has a breaking change.

Examples:

- Commit a new feature:

    ```
    feat(workspace): Publish static notebooks with live widgets
    ```

- Commit a bug fix:

    ```
    fix(core): Allow students to open submitted assignments from grades section
    ```

- Commit a version with a breaking change:

    ```
    feat(core): Deprecate observer role from group memberships

    BREAKING CHANGE: `extends` key in config file is now used for extending other config files
    ```

**Updating the Changelog Format**

Refer to the official `standard-version` docs to update the `CHANGELOG.md` template with additional options.

## Copyright and license

Copyright © 2019 IllumiDesk. All rights reserved, except as follows. Code
is released under the BSD 3.0 license. The README.md file, and files in the
"docs" folder are licensed under the Creative Commons Attribution 4.0
International License under the terms and conditions set forth in the file
"LICENSE.docs". You may obtain a duplicate copy of the same license, titled
CC-BY-SA-4.0, at http://creativecommons.org/licenses/by/4.0/.
