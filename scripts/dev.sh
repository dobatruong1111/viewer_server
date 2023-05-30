#!/bin/sh

# Start required services
sh scripts/dev-server.sh & sh scripts/dev-client.sh && kill $!;