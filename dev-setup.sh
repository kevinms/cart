#!/bin/bash

apt-get install python-pip
pip install tornado

ufw status
ufw allow 8888/tcp
ufw allow ssh
ufw enable

#
# To find the raw barcode scanner input device:
#
readlink -f $(ls -1 /dev/input/by-id/* | grep Electron_Company)


#
# If you download the GTIN POD database in CSV form:
#
#   http://pod.opendatasoft.com/explore/dataset/pod_gtin/export/
#
# The lines are seperate by Windows line endings '\r\n'. This
# messes up the import script, so run this command:
#
#   cat pod_gtin.csv | tr -d '\n' | tr '\r' '\n' > pod_gtin-sanitized.csv
#
# Next, we prune away most of the columns:
#
#   cat pod_gtin-sanitized.csv | cut -d';' -f1,2 > pod_gtin-pruned.csv
#
