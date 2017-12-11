docker --version
export PATH=$PATH:$HOME/.local/bin # put aws in the path
export PYTHONPATH=`pwd`:$PYTHONPATH
export DJANGO_SETTINGS_MODULE="appdj.settings.test"
export REDIS_URL="redis://localhost:6379/0"
export DATABASE_URL="postgres://postgres:@localhost:5432/travis_ci_test"
export NVIDIA_DOCKER_HOST=http://localhost:3476
export AWS_DEFAULT_REGION="us-west-2"
export COVERAGE_PROCESS_START=".coveragerc"