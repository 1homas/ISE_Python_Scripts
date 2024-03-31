#!/bin/bash
#
# Simple URL monitoring script.
#
# Requires setting the these environment variables using the `export` command:
#   export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
#   export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
#   export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
#   export ISE_CERT_VERIFY=false          # validate the ISE certificate
#
# You may add these export lines to a text file and load with `source`:
#   source ise-env.sh

SERVER=$ISE_HOSTNAME
USERNAME=$ISE_REST_HOSTNAME
PASSWORD=$ISE_REST_PASSWORD
HEADER_XML='Accept: application/xml'
HEADER_JSON='Accept: application/json'
HEADER=$HEADER_JSON
# URI=/ers/config/internaluser
# URI=/ers/config/adminuser
URI=/
SLEEP=5

while [ 1 ]; do

    date
    curl -k \
        --connect-timeout 3 \
        --max-time 10 \
        --location \
        --header "${HEADER}" \
        --head \
        --user $USERNAME:$PASSWORD \
        --request GET https://${SERVER}${URI}
    printf "_____\n"
    sleep $SLEEP

done