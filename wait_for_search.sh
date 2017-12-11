#!/bin/bash
# wait_for_search.sh

set -e

cmd="$@"
echo "Attempting to reach $ELASTICSEARCH_URL"
max_attempts=60
attempt=0
until $(curl --output /dev/null --silent --head --fail $ELASTICSEARCH_URL) || [ $attempt -eq $max_attempts ]; do
    sleep 1
    let attempt+=1
done

if [ $attempt -eq $max_attempts ]
then
    echo "Timed out looking for $ELASTICSEARCH_URL"
    exit 1
fi

echo "$ELASTICSEARCH_URL is up"