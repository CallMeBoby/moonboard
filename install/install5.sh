#!/bin/bash


echo "Prepare logfiles"
sudo touch /var/log/moonboard
sudo chown bob:bob /var/log/moonboard
sudo chown bob:bob /var/log/moonboard

# Prepare phase 2 to run at boot
sudo cp --verbose /home/bob/moonboard/services/moonboard-install.service /lib/systemd/system/moonboard-install.service
sudo chmod 644 /lib/systemd/system/moonboard-install.service
sudo systemctl daemon-reload
sudo systemctl enable moonboard-install.service

echo "Restarting in 5 seconds to finalize changes. CTRL+C to cancel."
sleep 1 > /dev/null
printf "."
sleep 1 > /dev/null
printf "."
sleep 1 > /dev/null
printf "."
sleep 1 > /dev/null
printf "."
sleep 1 > /dev/null
printf " Restarting"
sudo shutdown -r now