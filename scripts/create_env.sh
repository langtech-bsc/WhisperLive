#!/bin/bash

[ -d ".venv" ] && rm -fr ".venv"
python3 -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir -e .