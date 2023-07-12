docker build -t itech/apache2 .

docker run -d -it --rm --name itech-apache2 -p 8081:80 -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":/etc/apache2/sites-available/000-default.conf -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":/proxy/proxy-mapping.txt itech/apache2
