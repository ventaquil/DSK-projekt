#!/usr/bin/env bash

if [ -z $1 ]
then
    echo "Pass service name as argument"

    exit 1
fi

SERVICE_PORT=$(echo "$1" | tr "[:lower:]" "[:upper:]")
SERVICE_PORT+="_PORT"

env $SERVICE_PORT=80 docker-compose up -d $1

