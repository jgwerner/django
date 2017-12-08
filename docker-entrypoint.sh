#!/bin/sh

set -e

sleep 1
/srv/env/bin/python /srv/app/manage.py migrate
/srv/env/bin/python /srv/app/manage.py create_admin --username "$TEST_USER" --email "$TEST_USER_EMAIL" --password "$TEST_USER_PASSWORD"
/srv/env/bin/python /srv/app/manage.py create_server_size
/srv/env/bin/python /srv/app/manage.py site_host
/srv/app/watchman_trigger.sh

exec "$@"
