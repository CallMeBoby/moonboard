#!/bin/bash
# FIXME: installdir
echo "Install DBUS service"
sudo cp /home/bob/moonboard/ble/com.moonboard.conf /etc/dbus-1/system.d
cd /home/bob/moonboard/ble
sudo /home/bob/moonboard/services/install_service.sh com.moonboard.service > /tmp/moonboard-service-install.log

# Remove phase 2 from boot
sudo systemctl disable moonboard-install.service
sudo systemctl start moonboard.service 
