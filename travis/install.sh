if [ "$TEST_SUITE" = "UNIT" ]
then
    pip install -U pip setuptools wheel
    pip install -r requirements/dev.txt
    pip install codecov
fi