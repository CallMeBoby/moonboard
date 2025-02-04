#!/bin/bash

echo "Install services" # FIXME
cd /home/bob/moonboard/ble
make install_dbus
cd ..

cd /home/bob/moonboard/led
make install 
cd ..
