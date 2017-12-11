#!/bin/bash
# wait_for_api.sh

set -e

cmd="$@"
url="$HOST:$PORT/tbs-status"
echo "Attempting to reach $url"
max_attempts=30
attempt=0
until $(curl --output /dev/null --silent --head --fail $url) || [ $attempt -eq $max_attempts ]; do
    sleep 1
    let attempt+=1
done

if [ $attempt -eq $max_attempts ]
then
    echo "Timed out looking for $url"
    exit 1
fi

>&2 echo "$url is up"
exec $cmd