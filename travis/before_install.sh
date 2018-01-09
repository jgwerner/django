set -e

if [ "$TEST_SUITE" = "API" ]
then
    export DJANGO_SETTINGS_MODULE="appdj.settings.api_test"
    sudo rm /usr/local/bin/docker-compose
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    chmod +x docker-compose
    sudo mv docker-compose /usr/local/bin    
    docker-compose --version
elif [ "$TEST_SUITE" = "UNIT" ]
then
    export DJANGO_SETTINGS_MODULE="appdj.settings.test"
fi
docker --version