#!/bin/sh

cd "$(dirname "$(readlink -f "$0")")"

prospector ./*.py
mypy --py2 --ignore-missing-imports ./*.py
mypy --ignore-missing-imports ./*.py
python2 -m py.test --cov-branch --cov=. --cov-report=term-missing
python3 -m py.test --cov-branch --cov=. --cov-report=term-missing
