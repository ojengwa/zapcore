#!/bin/bash

# Node.js: grep the version from a package.json file with jq
PACKAGE_VERSION=$(cat client/package.json \
  | grep version \
  | head -1 \
  | awk -F: '{ print $2 }' \
  | sed 's/[",]//g' \
  | tr -d '[[:space:]]')

echo $PACKAGE_VERSION
