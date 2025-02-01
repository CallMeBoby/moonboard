#!/bin/bash

# Installing python dependencies
echo "Installing python dependencies"
pip3 install -r install/requirements.txt --break-system-package
sudo pip3 install -r install/requirements.txt 
# pip3 uninstall -y -r install/requirements.txt # uninstall
