#!/bin/bash
#
# simple URL monitoring script
#
SERVER=$ISE_HOSTNAME
USERNAME=$ISE_REST_HOSTNAME
PASSWORD=$ISE_REST_PASSWORD
HEADER_XML='Accept: application/xml'
HEADER_JSON='Accept: application/json'
HEADER=$HEADER_JSON
URI=/ers/config/internaluser
URI=/ers/config/adminuser
URI=/

while [ 1 ]; do

    date
    curl -k \
        --connect-timeout 3 \
        --max-time 10 \
        --location \
        --header "${HEADER}" \
        --head \
        --user $ISE_REST_USERNAME:$ISE_REST_PASSWORD \
        --request GET https://${SERVER}${URI}
    printf "_____\n"
    sleep 5

done