#!/bin/bash

SCRIPT_NAME=$0
DIR_NAME=$(realpath $(dirname $0))
DELIMITER="####################"


validate_variable(){

    local VARIABLE_NAME=$1
    local VARIABLE=$2
    echo "$VARIABLE_NAME: $VARIABLE"
    [ -z $VARIABLE ] && echo -e "$DELIMITER\n[$SCRIPT_NAME] ERROR: $VARIABLE_NAME variable not defined\nIt should be exported before running the script)\nExiting...\n$DELIMITER" && exit

}

validate_variable ASR_PORT $ASR_PORT 
validate_variable FASTAPI_PORT $FASTAPI_PORT
# validate_variable HTML_PORT $HTML_PORT

echo "Launching ASR server, HTML testing frontend and FastAPI..."
echo -e "\tConfiguration: ASR_PORT=${ASR_PORT}, FASTAPI_PORT=${FASTAPI_PORT}"

python3 run_server_api.py --port ${ASR_PORT} &
# bash $DIR_NAME/launch_http_frontend.sh ${HTML_PORT} &
fastapi dev main.py --host 0.0.0.0 --port ${FASTAPI_PORT}