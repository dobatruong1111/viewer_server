#!/bin/sh

poetry install;

# Install react-client dependencies

cd ./src/module/react-client/;
yarn install;