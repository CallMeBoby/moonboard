#!/bin/bash


echo "Enable SPI"
sudo sed -i 's/\#dtparam=spi=on/dtparam=spi=on/g' /boot/config.txt

echo "Disable Audio"
sudo sed -i 's/\dtparam=audio=on/#dtparam=audio=on/g' /boot/config.txt
sudo echo blacklist snd_bcm2835 > /etc/modprobe.d/raspi-blacklist.conf # FIXME: defensive

