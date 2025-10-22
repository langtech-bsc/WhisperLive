#!/bin/bash

TAG=$1
[ -z $TAG ] && echo -e "Usage: $0 <tag>\nExample: $0 v1.0.0\nExiting..." && exit

function docker_login {
    docker login registry.gitlab.bsc.es
}

function docker_logout {
    docker logout registry.gitlab.bsc.es
}

function push_image {
    docker tag $1 $2
    docker push $2
    echo "Pushed image: $2"
}

function remove_image {

    local IMAGE_TO_REMOVE=$1
    
    if [ ! -z "$(docker images -q $IMAGE_TO_REMOVE 2> /dev/null)" ]; then 
        docker rmi $IMAGE_TO_REMOVE
        echo "Removed local image: $IMAGE_TO_REMOVE"
    else
        echo "Local image $IMAGE_TO_REMOVE not found, skipping removal"
    fi
}

REGISTRY=registry.gitlab.bsc.es/lang-tech-unit/innovation/renfe/mvp

docker_login
LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu
# Semantic versioning
CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:$TAG
remove_image $CLOUD_IMAGE
push_image $LOCAL_IMAGE $CLOUD_IMAGE
# SHA versioning
# TAG=$(git rev-parse --short HEAD)
# CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:$TAG
# docker rmi $CLOUD_IMAGE
# push_image $LOCAL_IMAGE $CLOUD_IMAGE

# LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu-asr
# CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:latest
# docker rmi $CLOUD_IMAGE
# push_image $LOCAL_IMAGE $CLOUD_IMAGE

# LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu-fastapi
# CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:latest
# docker rmi $CLOUD_IMAGE
# push_image $LOCAL_IMAGE $CLOUD_IMAGE

docker_logout
