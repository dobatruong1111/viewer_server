#!bin/sh

# Load environments
export $(cat .env | xargs);

# Start Apache Service if not run already
#docker run -d -it --rm --name itech-apache2 -p 8081:80 -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":/etc/apache2/sites-available/000-default.conf -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":/proxy/proxy-mapping.txt itech/apache2

# Start 3D Server
# poetry run python src/module/vtkserver/vtk_server.py --port $SERVER_PORT;