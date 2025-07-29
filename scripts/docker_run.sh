#!/bin/bash

cmd="docker run -it -p 9090:9090 renfe-whisperlive-gpu"
echo $cmd && eval $cmd

