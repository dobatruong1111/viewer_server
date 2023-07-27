#!bin/sh

# Load environments
export $(cat .env | xargs);

PORT_APACHE=$(echo ${PORT_APACHE})
PORT_MAPPING="$PORT_APACHE:80"

APACHE_CONFIG_PATH=/etc/apache2/sites-available/000-default.conf
PROXY_MAPPING_PATH=/proxy/proxy-mapping.txt

# Start Apache Service if not run already
if [ "$(docker ps | grep itech-apache2)" = "" ]
then
    # Apache Config
    poetry run python viewerserver/module/3dserver/settings/apache_config.py --config ./viewerserver/module/3dserver/apache2/000-default.conf

    # Run the image on debian, ubuntu
    # docker run -d -it --rm --name itech-apache2 -p ${PORT_MAPPING} -v ./viewerserver/module/3dserver/apache2/000-default.conf:${APACHE_CONFIG_PATH} -v ./viewerserver/module/3dserver/proxy/proxy-mapping.txt:${PROXY_MAPPING_PATH} itech/apache2

    # Run the image on window
    # docker run -d -it --rm --name itech-apache2 -p $PORT_MAPPING -v (absolute path to 000-default.conf):${APACHE_CONFIG_PATH} -v (absolute path to proxy-mapping.txt):${PROXY_MAPPING_PATH} itech/apache2
    docker run -d -it --rm --name itech-apache2 -p ${PORT_MAPPING} -v "D:\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":${APACHE_CONFIG_PATH} -v "D:\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":${PROXY_MAPPING_PATH} itech/apache2

    echo "Apache Server is running"
fi

# Launcher Config
poetry run python viewerserver/module/3dserver/settings/launcher_config.py --config ./viewerserver/module/3dserver/config.json

# Start Launcher Service
poetry run python -m wslink.launcher ./viewerserver/module/3dserver/config.json