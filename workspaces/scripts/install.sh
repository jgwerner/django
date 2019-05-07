#!/bin/bash

build_dev_workspaces () {
    cd $HOME/build/IllumiDesk/app-backend/workspaces/
    make dev-env
    pip install -U pytest
}

main () {
    echo "Build development version of Jupyter workspaces ..."
    build_dev_workspaces
}
        