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
}

REGISTRY=registry.gitlab.bsc.es/lang-tech-unit/innovation/renfe/mvp

docker_login
LOCAL_IMAGE=whisperlive-renfe-whisperlive-gpu
CLOUD_IMAGE=$REGISTRY/$LOCAL_IMAGE:latest
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
