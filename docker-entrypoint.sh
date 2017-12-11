#!/bin/sh

set -e

source /srv/app/wait_for_search.sh

/srv/env/bin/python /srv/app/manage.py migrate
/srv/env/bin/python /srv/app/manage.py create_admin
/srv/env/bin/python /srv/app/manage.py create_server_size
/srv/env/bin/python /srv/app/manage.py site_host
/srv/app/watchman_trigger.sh

exec "$@"
