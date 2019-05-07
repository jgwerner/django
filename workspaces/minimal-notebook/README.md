# illumidesk/minimal-notebook

illumidesk/minimal-notebook is a community maintained Jupyter Notebook image.

## What It Includes

This image is uses `[jupyter/minimal-notebook](https://github.com/jupyter/docker-stacks/minimal-notebook) as the base image.

The basics:

- [Miniconda Python 3](https://www.anaconda.com/distribution/)

## Run

The basics:

    docker run -d -p 8080:8080 illumidesk/minimal-notebook

## Build

Build the image:

    docker build \
      --build-arg JUPYTER_LTI_VERSION=1.2.1 \
      -t illumidesk/minimal-notebook .

> Build argument for `JUPYTER_LTI_VERSION` defaults to `latest`.

## Verify Environment Settings

Open `env_test.ipynb` and run the cells to verify environment settings.

## Additional Options

Refer to [these docs for additional configuration options](https://jupyter-docker-stacks.readthedocs.io/en/latest/).