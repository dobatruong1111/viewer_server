#!/bin/sh

# Start required services, when the user hit Ctrl+C all services will be killed
sh scripts/dev-2d-server.sh & sh scripts/dev-3d-server.sh && kill $!;