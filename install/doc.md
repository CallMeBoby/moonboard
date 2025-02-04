# Intallazione 
1) raspberry make sure the host is **`raspi-moonboard`**
2) verify in file hosts **`127.0.1.1       raspi-moonboard`**
3) the user must be called **bob**
4) `git clone https://github.com/CallMeBoby/moonboard.git`
5) `./moonboard/install/install/10-prepare-raspi.sh`
6) `sudo vi /etc/mosquitto/mosquitto.conf` and add 
 
```
listener 1883
allow_anonymous true
```
7) `./moonboard/install/install/20-prepare-python.sh`
8) `./moonboard/install/install/30-install-service.sh`

