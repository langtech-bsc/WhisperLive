#!/bin/bash

COMPOSE_FILE="docker-compose.yml"

cmd="docker compose -f $COMPOSE_FILE up --build"

echo $cmd
eval $cmd