#!/bin/bash

uv run mypy --check-untyped-defs --explicit-package-bases --exclude 'bytecode/' plox
if [ $? -ne 0 ]; then
  exit 1
fi

if [ -d "tests" ] && [ -n "$(find tests -type f -name '*.py' -print -quit)" ]; then
    uv run pytest --verbose
fi
if [ $? -ne 0 ]; then
  exit 1
fi


if [ -f "real-tests/script.py" ]; then
    python3 ./real-tests/script.py plox
fi
if [ $? -ne 0 ]; then
  exit 1
fi

STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.py$' | xargs)

uv format
if [ $? -ne 0 ]; then
  echo "Code formatting failed. Please fix the issues and stage the changes before committing."
  exit 1
fi

if [ -n "$STAGED_PY_FILES" ]; then
    git add $STAGED_PY_FILES
fi
