#!/bin/bash

build_dev_workspaces () {
    cd $HOME/build/IllumiDesk/illumidesk/workspaces/
    make dev-env
    pip install -U pytest
}

main () {
    echo "Build development version of Jupyter workspaces ..."
    build_dev_workspaces
}
        