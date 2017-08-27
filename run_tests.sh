#!/bin/sh

cd "$(dirname "$(readlink -f "$0")")"

prospector saveswap.py
mypy --py2 --ignore-missing-imports saveswap.py
mypy --ignore-missing-imports saveswap.py
python2 -m py.test --cov-branch --cov=. --cov-report=term-missing saveswap.py
python3 -m py.test --cov-branch --cov=. --cov-report=term-missing saveswap.py
