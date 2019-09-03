# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# Copyright (c) IllumiDesk.
# Distributed under the terms of the Modified BSD License.

# set up base image arg
ARG BASE_IMAGE=jupyter/datascience-notebook
FROM $BASE_IMAGE

LABEL maintainer="IllumiDesk <hello@illumidesk.com>"

ARG JUPYTER_LTI_VERSION=@illumidesk/jupyter-lti@latest

# set explicitly just in case
USER $NB_UID

# Install conda-build, update conda and pip
RUN conda install conda-build &&\
    conda update -n base conda && \
    conda update conda-build && \
    conda install pip

# Create a Python 2.x environment 
RUN conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 \
    ipython \
    ipykernel \
    kernda && \
    conda build purge-all

USER root

# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
    $CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json

USER $NB_UID

# install jupyter-lti extension
RUN jupyter labextension install $JUPYTER_LTI_VERSION

# Install Tensorflow
RUN conda install --quiet --yes \
    'tensorflow=1.13*' \
    'keras=2.2*' && \
    conda build purge-all && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Xeus Cling
RUN conda install -c conda-forge \
    xeus-cling && \
    conda build purge-all && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Additional pip packages
RUN pip install \
    bqplot \
    colour \
    cvxpy \
    ipympl \
    ipyvolume \
    nbgrader==0.6.0 \
    plotly==2.7 \
    voila && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# copy/install as root, then fix permissions for $NB_USER
USER root

COPY jupyter_notebook_config.py /etc/jupyter/
COPY nbgrader_config.py /etc/jupyter/
RUN mkdir -p /srv/nbgrader/exchange
RUN fix-permissions /srv/nbgrader/exchange/
RUN fix-permissions /etc/jupyter/
RUN fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

EXPOSE 8080

# set container to run with $NB_USER by default
USER $NB_UID
