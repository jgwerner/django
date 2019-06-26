#!/bin/bash

change_directory () {
    # Change into app-frontend root
    cd $HOME/build/IllumiDesk/illumidesk/app-frontend/
}

main () {
    change_directory
    echo "Run tests"
    npm run test -- --coverage a
}

main
