#!/bin/bash

mypy .
if [ $? -ne 0 ]; then
  exit 1
fi
