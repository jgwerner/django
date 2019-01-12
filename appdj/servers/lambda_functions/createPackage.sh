#!/bin/sh
if [ ! -d vendored ]; then
	mkdir vendored
	pip install requests -t ./vendored
fi
zip -9 stats.zip statistics.py
cd vendored
zip -rg9 --exclude=*.pyc --exclude=*__pycache__* ../stats.zip .
