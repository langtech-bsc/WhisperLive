#!/bin/bash

COMPOSE_FILE="docker-compose-pull-images.yml"
cmd="docker compose -f $COMPOSE_FILE up --build"

docker login registry.gitlab.bsc.es
echo $cmd
eval $cmd
docker logout registry.gitlab.bsc.es