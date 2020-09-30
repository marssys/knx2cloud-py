# knx2cloud-py
## Dependencies
- kDriveExpress SDK https://weinzierl.de/index.php/en/all-knx/software-tools-en/kdriveexpress-en (used for KNX communication)
- Eclipse Paho MQTT Python Client https://github.com/eclipse/paho.mqtt.python (used for MQTT communication)
## Install on Ubuntu 16.04 LTS
- `cd ~`
- `git clone https://github.com/marssys/knx2cloud-py.git` (`git pull`)
- `cd knx2cloud-py`
- `sudo cp kdriveExpress-lib/libkdriveExpress.so /usr/lib`
- `pip install paho-mqtt`
## Usefull commands
- `sudo apt-get update`
- `sudo apt-get upgrade`
- Set timezone `sudo dpkg-reconfigure tzdata` (check current time `date`)
- `sudo apt-get install python-pip`