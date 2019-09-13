#!/bin/bash

build_extension () {
    npm install rimraf -g
    npm install
    npm run build
}

main () {
    echo "Build Jupyter LTI extension ..."
    build_extension
}