set -e

if [ "$TEST_SUITE" = "UNIT" ]
then
    echo "listen_addresses = '*'" | sudo tee -a /etc/postgresql/9.*/main/postgresql.conf
    echo "host all all 0.0.0.0/0 trust" | sudo tee -a /etc/postgresql/9.*/main/pg_hba.conf
    sudo /etc/init.d/postgresql stop
    sudo /etc/init.d/postgresql start 9.4
    psql template1 -c 'CREATE EXTENSION IF NOT EXISTS hstore;' -U postgres
    psql -c 'create database travis_ci_test;' -U postgres
fi