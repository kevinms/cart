#!/bin/bash

apt-get install python-pip
pip install tornado

ufw status
ufw allow 8888/tcp
ufw enable
