#!/bin/bash

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

REGISTRY=registry.gitlab.bsc.es/lang-tech-unit/innovation/renfe/mvp

docker_login
LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu
# Semantic versioning
TAG=v1.0.0
CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:$TAG
docker rmi $CLOUD_IMAGE
push_image $LOCAL_IMAGE $CLOUD_IMAGE
# SHA versioning
TAG=$(git rev-parse --short HEAD)
CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:$TAG
docker rmi $CLOUD_IMAGE
push_image $LOCAL_IMAGE $CLOUD_IMAGE

# LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu-asr
# CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:latest
# docker rmi $CLOUD_IMAGE
# push_image $LOCAL_IMAGE $CLOUD_IMAGE

# LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu-fastapi
# CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:latest
# docker rmi $CLOUD_IMAGE
# push_image $LOCAL_IMAGE $CLOUD_IMAGE

docker_logout
