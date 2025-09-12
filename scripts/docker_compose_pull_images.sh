#!/bin/bash

# COMPOSE_FILE="docker-compose-pull-images-production.yml"
# ENV_FILE=".env-production-renfe"

COMPOSE_FILE="docker-compose-pull-images.yml"
ENV_FILE=".env"

# FUNCTIONS
show_env_file(){
    if [ -f "$ENV_FILE" ]; then
        echo "Using environment file: $ENV_FILE"
        echo -e "###################################\n"
        cat "$ENV_FILE"
        echo -e "\n#####################################"
    else
        echo "ERROR: Environment file $ENV_FILE does not exist. Exiting..." && exit 1
    fi
}

docker_compose(){

    cmd="docker compose --env-file $ENV_FILE -f $COMPOSE_FILE up --build"
    echo $cmd && eval $cmd

}

docker_login(){
    docker login registry.gitlab.bsc.es
}

docker_logout(){
    docker logout registry.gitlab.bsc.es
}

# MAIN
docker_login
show_env_file
docker_compose
docker_logout