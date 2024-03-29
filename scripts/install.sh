#!/bin/sh

# Install dependencies for python server
# pip install "uvicorn[standard]";
poetry install;

# Install react client
git submodule add --force https://gitlab+deploy-token-2165626:Y1z-u-HyBRPNCWczTKQ-@gitlab.com/itech-viewer/saola-dicom-viewer;
git submodule update --recursive --remote

# Install Apache if not exist.
if [ "$(docker images -q itech/apache2)" = "" ]
then
    docker build -t itech/apache2 ./viewerserver/module/3dserver/apache2
fi