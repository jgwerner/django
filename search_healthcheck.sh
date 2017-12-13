#!/bin/bash
# wait_for_search.sh

echo "Attempting to reach $ELASTICSEARCH_URL"
curl --output /dev/null --silent --head --fail $ELASTICSEARCH_URL) || exit 1
