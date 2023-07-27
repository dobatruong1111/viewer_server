#!bin/sh

# Load environments
export $(cat .env | xargs);

# Start 2D Server
poetry run uvicorn viewerserver.main:app --host $HOST --port $PORT_2DSERVER --workers $WORKERS;