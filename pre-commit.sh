#!/bin/bash

uv run mypy --check-untyped-defs --explicit-package-bases --exclude 'bytecode/' plox
if [ $? -ne 0 ]; then
  exit 1
fi

uv run pytest --verbose

if [ -d "real-tests" ]; then
    python3 real-tests/script.py
fi
if [ $? -ne 0 ]; then
  exit 1
fi
