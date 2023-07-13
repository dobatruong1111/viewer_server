docker build -t itech/apache2 .

docker run -d -it --rm --name itech-apache2 -p 8081:80 -v (absolute path to 000-default.conf):/etc/apache2/sites-available/000-default.conf -v (absolute path to proxy-mapping.txt):/proxy/proxy-mapping.txt itech/apache2
