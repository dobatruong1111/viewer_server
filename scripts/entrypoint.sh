#!/bin/sh

# Load environments
export $(cat .env | xargs);

# Restart apache2
echo "Restarting apache2..."
service apache2 restart

# Install dependencies
echo "Installing dependencies..."
poetry install

# Starting Server
echo "Starting Server..."
poetry run uvicorn viewerserver.main:app --host ${HOST} --port ${PORT_2DSERVER} --workers ${WORKERS} & python -m wslink.launcher /opt/viewer_server/config/launcher/config.json