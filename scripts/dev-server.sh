#!bin/sh

# Load environments
export $(cat .env | xargs);

# Start VTK Server
poetry run python src/module/vtkserver/vtk_server.py --port $SERVER_PORT;