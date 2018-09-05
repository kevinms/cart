#!/bin/bash

# sudo crontab -e
# @reboot /home/pi/cart/run.sh > /home/pi/cart/run.log 2>&1

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

#sudo python scan.py -s '192.168.0.2:8888' -d $(readlink -f $(ls -1 /dev/input/by-id/* | grep Electron_Company))
#sudo python scan.py -s debrislabs.com:8888 -d $(readlink -f $(ls -1 /dev/input/by-id/* | grep Electron_Company))
sudo python $DIR/scan.py -s debris.duckdns.org:8888 -d $(readlink -f $(ls -1 /dev/input/by-id/* | grep Electron_Company))

