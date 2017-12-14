if [ "$TEST_SUITE" = "UNIT" ]
then
    bash <(curl -s https://codecov.io/bash)
fi