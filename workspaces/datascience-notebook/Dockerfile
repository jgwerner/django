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

# Install pip
RUN conda install -c anaconda pip -y

# Create a Python 2.x environment 
RUN conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 \
    ipython \
    ipykernel \
    kernda

# Install Tensorflow
RUN conda install --quiet --yes \
    'tensorflow=1.13*' \
    'keras=2.2*' && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# Additional packages
RUN conda install -c conda-forge -y \
    bqplot \
    colour \
    cvxpy \
    ipympl \
    ipyvolume \
    ipywidgets==7.5.* \
    jupyter_nbextensions_configurator \
    plotly==2.7 \
    pythreejs \
    nbgrader

# install nbextension for classic notebooks with conda
# https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html#conda
RUN conda install -c conda-forge \
    jupyter_contrib_nbextensions \
    widgetsnbextension -y

# install widgets and illumidesk lti extensions for jupyterlab
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    jupyter labextension install $JUPYTER_LTI_VERSION

# copy to dir used by --sys-prefix flag, enable extension
# this operation assumes that contents from the repo's jupyter-lti/ folder have
# been copied to the workspaces/datascience-notebook/illumidesk-lti/ folder.
RUN mkdir -p $CONDA_DIR/share/jupyter/nbextensions/illumidesk_lti/
COPY illumidesk_lti/ $CONDA_DIR/share/jupyter/nbextensions/illumidesk_lti/
RUN jupyter nbextension enable illumidesk_lti/illumidesk_lti

# copy/install as root, then fix permissions for $NB_USER
USER root

# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
    $CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json

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