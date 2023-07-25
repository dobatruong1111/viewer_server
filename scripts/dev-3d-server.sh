#!bin/sh

# Load environments
export $(cat .env | xargs);

# Start Apache Service if not run already
# docker run -d -it --rm --name itech-apache2 -p 8081:80 -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":/etc/apache2/sites-available/000-default.conf -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":/proxy/proxy-mapping.txt itech/apache2
if [ "$(docker ps | grep itech-apache2)" = "" ]
then
    # Run the image on debian, ubuntu
    # docker run -d -it --rm --name itech-apache2 -p 8081:80 -v ./viewerserver/module/3dserver/apache2/000-default.conf:/etc/apache2/sites-available/000-default.conf -v ./viewerserver/module/3dserver/proxy/proxy-mapping.txt:/proxy/proxy-mapping.txt itech/apache2

    # Run the image on window
    # docker run -d -it --rm --name itech-apache2 -p 8081:80 -v (absolute path to 000-default.conf):/etc/apache2/sites-available/000-default.conf -v (absolute path to proxy-mapping.txt):/proxy/proxy-mapping.txt itech/apache2
    docker run -d -it --rm --name itech-apache2 -p 8081:80 -v "D:\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":/etc/apache2/sites-available/000-default.conf -v "D:\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":/proxy/proxy-mapping.txt itech/apache2

    echo "Apache Server is running"
fi

# Start Launcher Service
poetry run python -m wslink.launcher ./viewerserver/module/3dserver/config.json