#!/bin/bash

uv run mypy --check-untyped-defs plox
if [ $? -ne 0 ]; then
  exit 1
fi
