#!/bin/bash
# setup.sh
cat > .env <<EOF
WORKDIR=$HOME
DOCKER_SOCK=/run/user/$(id -u)/docker.sock
EOF
echo ".env created for user $USER"
