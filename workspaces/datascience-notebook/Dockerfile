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

# Install Tensorflow
RUN conda install --quiet --yes \
    'tensorflow=1.13*' \
    'keras=2.2*' && \
    conda build purge-all

# Xeus Cling
RUN conda install -c conda-forge \
    xeus-cling && \
    conda build purge-all

# Additional pip packages
RUN pip install -v \
    bqplot \
    colour \
    cvxpy \
    ipympl \
    ipyvolume \
    ipywidgets==7.5.* \
    jupyter_nbextensions_configurator \
    plotly==2.7

# install nbextension for classic notebooks with conda
# https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html#conda
RUN conda install -c conda-forge jupyter_contrib_nbextensions -y
RUN mkdir -p $CONDA_DIR/share/jupyter/nbextensions/illumidesk_lti/
    
# copy to dir used by --sys-prefix flag, enable extension
ADD illumidesk_lti/. $CONDA_DIR/share/jupyter/nbextensions/illumidesk_lti/
RUN jupyter nbextension enable illumidesk_lti/illumidesk_lti

# install nbgrader with conda
RUN conda install -c conda-forge nbgrader

USER root

# jupyter and nbgrader config
COPY jupyter_notebook_config.py /etc/jupyter/
COPY nbgrader_config.py /etc/jupyter/

# not necessary, but removes error in formgrader tab
RUN mkdir -p /srv/nbgrader/exchange
RUN fix-permissions /srv/nbgrader/exchange/ && \
    fix-permissions /etc/jupyter/ && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

EXPOSE 8080

# set container to run with $NB_USER by default
USER $NB_UID
