# Viewer-Server

A viewer server is a radiological viewer developed for clinical professionals.

## Setup Docker

[Install Docker](https://docs.docker.com/engine/install/)

## Setup Native

1. Clone project và sửa trường HOST thành địa chỉ IP máy trong tệp .env

2. Xóa thư mục saola-dicom-viewer và chạy tệp install.sh

```
rmdir saola-dicom-viewer

sh scripts/install.sh
```

3. Sửa lại đường dẫn mapping tệp khi chạy apache trên docker trong tệp scripts/dev-3d-server.sh tương ứng với hệ điều hành đang sử dụng.

4. Start viewer server (chạy lại nếu có lỗi)

```
sh scripts/dev.sh
```

5. Gọi API lấy link

```
{
    "userId":"123",
    "expireIn":600,
    "studyUIDs": {
        "1.2.840.113619.2.417.3.2831163337.337.1669159714.820": {
            "url": "http://27.72.147.196:37000/orthanc/wado-rs",
            "authentication": "Basic b3J0aGFuYzpvcnRoYW5j"
        }
    }
}
```

## Build Docker

1. Clone project và sửa trường HOST trong tệp .env

```
HOST=0.0.0.0
PORT_2DSERVER=8000
PORT_APACHE=8081
PORT_LAUNCHER=9000
WORKERS=4
```

2. Xóa thư mục saola-dicom-viewer và lấy bản React client mới về

```
rmdir saola-dicom-viewer

git submodule add --force https://gitlab+deploy-token-2165626:Y1z-u-HyBRPNCWczTKQ-@gitlab.com/itech-viewer/saola-dicom-viewer

git submodule update --recursive --remote
```

3. Build Docker

```
docker build -t viewer-server -f Dockerfile .
```

4. Run Container

```
docker run --rm --name viewerserver -p 8081:8081 -p 8000:8000 -p 9000:9000 --gpus all -it viewer-server
```

5. Start viewer server (chạy lại nếu có lỗi)

```
sh entrypoint.sh
```

6. Gọi API lấy link

```
{
    "userID":"123",
    "expireIn":600,
    "studyUIDs": {
        "1.2.840.113619.2.417.3.2831163337.337.1669159714.820": {
            "url": "http://27.72.147.196:37000/orthanc/wado-rs",
            "authentication": "Basic b3J0aGFuYzpvcnRoYW5j"
        }
    }
}
```

7. Thoát docker bash

```
exit
```

## Development

Debian, Ubuntu you may need to run below command if install failed

```shell
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```

To run the project with pre-built viewer client, run this command

```shell
sh scripts/dev-server.sh
```

To manually compile the viewer client and run for development on the viewer client, run this command

```shell
sh scripts/build-client.sh
sh scripts/dev.sh
```
