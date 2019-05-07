#!/bin/bash

conda_jupyterlab () {
    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O ~/miniconda.sh;
    bash ~/miniconda.sh -b -p $HOME/miniconda
    export PATH="$HOME/miniconda/bin:$PATH"
    pip install --pre jupyterlab
}

main () {
    echo "Install conda and JupyterLab ..."
    conda_jupyterlab
}
