# 3D Viewer-Server

## Cấu Hình Launcher Service

IP máy

```
$ hostname -I
```

```
config.json

{
    "configuration": {
        "host": "192.168.1.190",    <--- Sửa đổi theo địa chỉ IP máy chủ
        "port": 9000,               <--- Cổng để chạy Launcher Service
        "endpoint": "viewer",
        "log_dir": "./launcher",                    <--- Thư mục Log: chứa các tệp id.txt lưu log khi chạy process server
        "proxy_file": "./proxy/proxy-mapping.txt",  <--- Lưu trữ id, host:port của process server
        "sessionURL": "ws://192.168.1.190:8081/proxy?sessionId=${id}&path=ws",  <--- Kết nối Websocket thông qua sessionURL
        "timeout": 25,
        "sanitize": {},
        "fields": []
    },
    "resources": [
        {
            "host": "192.168.1.190",    <--- Sửa đổi theo địa chỉ IP máy chủ
            "port_range": [9001, 9500]  <--- Các cổng để chạy các process server
        }
    ],
    "properties": {},
    "apps": {
        "viewer": {
            "cmd": [
                "poetry",
                "run",
                "python",
                "vtk_server.py",
                "--host",
                "${host}",
                "--port",
                "${port}",
                "--authKey",
                "${secret}",
                "--studyUUID",
                "${studyUUID}",
                "--seriesUUID",
                "${seriesUUID}"
            ],
            "ready_line": "Starting factory"
        }
    }
}
```

## Cấu Hình Apache Server

```
apache2/000-default.conf

<VirtualHost *:80>
    DocumentRoot /deploy/server/www

    <Directory /deploy/server/www>
        Options Indexes FollowSymLinks
        Order allow,deny
        Allow from all
        AllowOverride None
        Require all granted
    </Directory>

    Header always set Access-Control-Allow-Origin "*"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header always set Access-Control-Allow-Headers "*"
    Header always set Access-Control-Allow-Credentials "true"

    # Handle Request Method: OPTIONS
    RewriteEngine On
    RewriteCond %{REQUEST_METHOD} OPTIONS
    RewriteRule ^(.*)$ $1 [R=204,L]

    # Handle launcher forwarding
    ProxyPass /launcher http://192.168.1.190:9000/viewer    <--- Request đến Launcher Service
    ProxyPass /viewer http://192.168.1.190:9000/viewer      <--- Request đến Launcher Service

    # Handle WebSocket forwarding
    RewriteEngine On
    RewriteMap session-to-port txt:/proxy/proxy-mapping.txt
    RewriteCond %{QUERY_STRING} ^sessionId=(.*)&path=(.*)$ [NC]
    RewriteRule ^/proxy.*$  ws://${session-to-port:%1}/%2  [P]

</VirtualHost>
```

## Cài Docker

[Install Docker](https://docs.docker.com/engine/install/)

## Run

### Run Apache Server

Build the image

```
docker build -t itech/apache2 .
```

Run the image on port 8081
Replace 000-default.conf path and proxy-mapping.txt path by your exactly paths

```
docker run -d -it --rm --name itech-apache2 -p 8081:80 -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\apache2\000-default.conf":/etc/apache2/sites-available/000-default.conf -v "C:\Users\DELL E5540\Desktop\viewer-server\viewerserver\module\3dserver\proxy\proxy-mapping.txt":/proxy/proxy-mapping.txt itech/apache2
```

### Run Launcher Service

```
poetry run python -m wslink.launcher config.json
```

### Requests

Example: POST Request

```
{
    "application": "viewer",
    "useUrl": true,
    "studyUUID": "1.2.840.113619.2.417.3.2831163337.337.1669159714.820",
    "seriesUUID": "1.2.840.113619.2.417.3.2831163337.337.1669159714.826.3"
}
```

Launcher Service: receive requests

```
http://192.168.1.190:8081/viewer/
```
