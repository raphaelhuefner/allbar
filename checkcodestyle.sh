#!/bin/bash

./bin/pycodestyle allbar/

./bin/flake8 --enable-extensions=naming allbar/

./bin/pylint allbar/
# ./bin/pylint -d empty-docstring allbar/app.py

./bin/pydocstyle --explain allbar/
# ./bin/pydocstyle --explain allbar/app.py


