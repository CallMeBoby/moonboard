#!/bin/bash

# Installing python dependencies # FIXME venv
echo "Installing python dependencies"
sudo pip3 install -r requirements.txt --break-system-packages
# --break-system-packages for disable OSsystem security