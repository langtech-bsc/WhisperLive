#!/bin/bash

echo "Launching ASR server and FastAPI..."
echo -e "\tConfiguration: ASR_PORT=${ASR_PORT}, FASTAPI_PORT=${FASTAPI_PORT}"

python3 run_server_api.py --port ${ASR_PORT} &
fastapi dev main.py --host 0.0.0.0 --port ${FASTAPI_PORT}