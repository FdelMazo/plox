#!/bin/bash

uv run mypy --check-untyped-defs --explicit-package-bases --exclude 'bytecode/' plox
if [ $? -ne 0 ]; then
  exit 1
fi

cd bytecode && uv run mypy --check-untyped-defs --explicit-package-bases .
if [ $? -ne 0 ]; then
  exit 1
fi
