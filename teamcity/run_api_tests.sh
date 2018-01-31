set -e

finish(){
    docker logs appbackend_test_1
    docker-compose -f docker-compose-test.yml stop
    docker-compose -f docker-compose-test.yml rm
}
trap finish EXIT

docker-compose -f docker-compose-test.yml -p appbackend up --build --abort-on-container-exit