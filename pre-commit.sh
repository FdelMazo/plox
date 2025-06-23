#!/bin/bash

mypy . --explicit-package-bases --check-untyped-defs --exclude 'bytecode/'
if [ $? -ne 0 ]; then
  exit 1
fi

cd bytecode && mypy . --explicit-package-bases --check-untyped-defs
if [ $? -ne 0 ]; then
  exit 1
fi
