[![Build Status](https://travis-ci.com/IllumiDesk/workspaces.svg?branch=master)](https://travis-ci.com/IllumiDesk/workspaces)

# IllumiDesk Workspaces

Workspace images for https://app.illumidesk.com.

Read more about these workspaces in our [docs](https://docs.illumidesk.com)

## Commands

    make help

# Env Vars

Environment variables used to build and push images to docker registry:

| Name                          | Description | Default Value |
|-------------------------------|-------------|---------------|
| IMAGE_NAME             | DockerHub image name. | None |
| OWNER_NAME               | DockerHub organization name. | None |
| DOCKER_PASSWORD               | DockerHub account password.| None |
| DOCKER_USER                   | DockerHub user account. | None |
| GITHUB_DEV_BRANCH             | GitHub dev branch. | None |
| GITHUB_PROD_BRANCH            | GitHub dev branch. | None |