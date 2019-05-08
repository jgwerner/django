[![Build Status](https://travis-ci.com/IllumiDesk/workspaces.svg?branch=master)](https://travis-ci.com/IllumiDesk/workspaces)

# IllumiDesk Workspaces

Workspace images for https://app.illumidesk.com.

Read more about these workspaces in our [docs](https://docs.illumidesk.com)

## Commands

    make help

## Build/Test Notes

By default all Dockerfiles set the Jupyter LTI extension to latest using `@illumidesk/jupyter-lti@latest`. To set a custom version for the Jupyter LTI extension for a docker image build set it with `DARGS`:

    DARGS="JUPYTER_LTI_VERSION=@1.2.4" make test/minimal-notebook

You may not need to build all images to run basic Jupyter Notebook tests. In these cases use the `TEST_ONLY_BUILD` to only build the `illumidesk/minimal-notebook` image:

    make build-test-all DARGS="--build-arg TEST_ONLY_BUILD=1"

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