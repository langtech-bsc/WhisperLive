#!/bin/bash

stop_containers(){

    echo -e "\nCurrent running containers:\n"
    docker ps

    container_list="$(docker ps | grep whisper | cut -f1 -d " " | paste -sd ' ')"
    echo "container_list: $container_list"
    if [ -z "$container_list" ]; then
        echo -e "\nNo running containers related to whisperlive found.\n"
    else
        echo -e "\nStopping all running containers related to whisperlive...\n"
        cmd="docker stop $container_list"
        echo -e "\n$cmd\n" && eval $cmd
        docker ps
    fi

}

remove_images(){

    echo -e "\nCurrent images:\n"
    docker images

    image_list="$(docker images | grep whisper | cut -f1 -d ' ' | paste -sd ' ')"
    echo "image_list: $image_list"
    if [ -z "$image_list" ]; then
        echo -e "\nNo images related to whisperlive found.\n"
    else
        echo -e "\nRemoving all images related to whisperlive...\n"
        cmd="docker rmi --force $image_list"
        echo -e "\n$cmd\n" && eval $cmd
    fi

}

system_prune(){

    echo -e "\nRemoving all dangling images...\n"
    cmd="docker system prune"
    echo -e "\n$cmd\n" && eval $cmd

}

show_containers_images(){

    echo -e "\nCurrent running containers:\n"
    docker ps

    echo -e "\nCurrent images:\n"
    docker images

}

### MAIN
stop_containers
remove_images
system_prune
show_containers_images