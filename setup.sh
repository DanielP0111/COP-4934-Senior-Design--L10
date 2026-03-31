#!/bin/bash
# setup.sh
mkdir -p $HOME/executor
chmod 777 $HOME/executor
cat > .env <<EOF
WORKDIR=$HOME/executor
DOCKER_SOCK=/run/user/$(id -u)/docker.sock
EOF
echo ".env created for user $USER"
