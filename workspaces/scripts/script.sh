#!/bin/bash

build_and_test () {
    cd $HOME/build/IllumiDesk/illumidesk/workspaces/
    make build-test-all DARGS="--build-arg TEST_ONLY_BUILD=1"
}

main () {
    build_and_test
}