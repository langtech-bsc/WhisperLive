# How can it be installed?

# Python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Troubleshooting: https://stackoverflow.com/a/77783437
# run this as root in the environment:
sudo apt-get update
sudo apt-get install python3-dev
pip install pyaudio
