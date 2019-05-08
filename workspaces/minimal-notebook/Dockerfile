# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# Copyright (c) IllumiDesk.
# Distributed under the terms of the Modified BSD License.

# set up base image arg
ARG BASE_IMAGE=jupyter/minimal-notebook
ARG JUPYTER_LTI_VERSION=latest
FROM $BASE_IMAGE

LABEL maintainer="IllumiDesk <hello@illumidesk.com>"

# base image should have $NB_UID already set, but set it
# explicitly just in case
USER $NB_UID

# install jupyter-lti extension
RUN jupyter labextension install @illumidesk/jupyter-lti@JUPYTER_LTI_VERSION

# copy/install as root, then fix permissions for $NB_USER
USER root

RUN conda install -c conda-forge nbgrader && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

COPY jupyter_notebook_config.py /etc/jupyter/
COPY env_test.ipynb $HOME/
RUN fix-permissions /etc/jupyter/
RUN fix-permissions $HOME/env_test.ipynb

EXPOSE 8080

# set container to run with $NB_USER by default
USER $NB_UID
