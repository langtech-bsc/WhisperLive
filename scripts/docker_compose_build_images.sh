#!/bin/bash

COMPOSE_FILE="docker-compose.yml"
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

clean_previous_images(){
    echo -e "\nCleaning up previous images related to whisperlive...\n"
    bash scripts/docker_clean.sh
}

# MAIN
show_env_file
#clean_previous_images
docker_compose