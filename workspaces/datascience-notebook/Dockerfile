# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# Copyright (c) IllumiDesk.
# Distributed under the terms of the Modified BSD License.

# set up base image arg
ARG BASE_IMAGE=jupyter/datascience-notebook
ARG JUPYTER_LTI_VERSION=latest
FROM $BASE_IMAGE

LABEL maintainer="IllumiDesk <hello@illumidesk.com>"

# Create a Python 2.x environment 
RUN conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 \
    ipython \
    ipykernel \
    kernda && \
    conda clean -tipsy

USER root

# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
    $CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json

USER $NB_UID

# Install Tensorflow for Python3
RUN conda install --quiet --yes \
    'tensorflow=1.12*' \
    'keras=2.2*' && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# install nodejs kernel
RUN conda install -c conda-forge nodejs
RUN npm install -g ijavascript
RUN ijsinstall

# Xeus Cling
RUN conda install -c conda-forge xeus-cling && \
    conda clean -tipsy && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

# install jupyter-lti extension
RUN jupyter labextension install @illumidesk/jupyter-lti@$JUPYTER_LTI_VERSION

# copy/install as root, then fix permissions for $NB_USER
USER root

COPY jupyter_notebook_config.py /etc/jupyter/
COPY env_test.ipynb $HOME/
RUN fix-permissions /etc/jupyter/
RUN fix-permissions $HOME/env_test.ipynb

EXPOSE 8080

# set container to run with $NB_USER by default
USER $NB_UID
