#!/bin/bash

echo "Install service" # FIXME
cd /home/bob/moonboard/services
sudo ./install_service.sh moonboard.service 
cd /home/bob/moonboard


echo "Install DBUS service"
sudo cp /home/bob/moonboard/ble/com.moonboard.conf /etc/dbus-1/system.d
sudo cp /home/bob/moonboard/ble/com.moonboard.service /usr/share/dbus-1/system-services/
