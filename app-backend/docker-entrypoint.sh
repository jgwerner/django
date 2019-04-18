#!/bin/sh

set -e

sleep 1

/srv/env/bin/python /srv/app/manage.py migrate
/srv/env/bin/python /srv/app/manage.py create_server_size
/srv/env/bin/python /srv/app/manage.py site_host
/srv/env/bin/python /srv/app/manage.py create_iam_users

exec "$@"
