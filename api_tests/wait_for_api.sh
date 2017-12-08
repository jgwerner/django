#!/bin/bash
# wait-for-postgres.sh

set -e

cmd="$@"
url="$HOST:$PORT/tbs-status"
echo "Attempting to reach $url"
until $(curl --output /dev/null --silent --head --fail $url); do
    printf 'API is unavailable - continue to wait...'
    sleep 3
done

>&2 echo "API is up - executing command"
exec $cmd