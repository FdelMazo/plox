#!/bin/bash

uv run mypy --check-untyped-defs plox
if [ $? -ne 0 ]; then
  exit 1
fi

STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR -- '*.py' | xargs)

uv format --preview-features format
if [ $? -ne 0 ]; then
  echo "Code formatting failed. Please fix the issues and stage the changes before committing."
  exit 1
fi

if [ -n "$STAGED_PY_FILES" ]; then
    git add $STAGED_PY_FILES
fi
