# Viewer-Server

A viewer server is a radiological viewer developed for clinical professionals.

## Run

clone the project and run with command

```shell
sh scripts/install.sh
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
