#!/bin/bash

cmd="docker build -f docker/Dockerfile.gpu -t renfe-whisperlive-gpu ."
echo $cmd && eval $cmd
