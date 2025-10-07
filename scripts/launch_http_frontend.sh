#!/bin/bash

HTML_PORT=$1

SCRIPT_NAME=$0
SCRIPT_BASEFOLDER=$(realpath $(realpath .)/../)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
FRONTEND_FOLDER=$(realpath "$SCRIPT_DIR/../frontend4")
DELIMITER="####################"
pwd
[ -z $HTML_PORT ] && echo -e "$DELIMITER\n[$SCRIPT_NAME] ERROR: HTML_PORT variable not defined\nIt should be exported before running the script)\nExiting...\n$DELIMITER" && exit
[ ! -d $FRONTEND_FOLDER ] && echo -e "ERROR: frontend folder does not exist: $FRONTEND_FOLDER. Exiting..." && exit

cd $FRONTEND_FOLDER
cmd="python3 -m http.server $HTML_PORT"
msg=">> Launching HTML server:\n\t$cmd"
echo -e $msg && eval $cmd

