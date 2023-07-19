#!/usr/bin/env python3
"""
ciscoisesdk_test.py

Author: Thomas Howard, thomas@cisco.com
"""

import argparse
import requests
import json
import os
import sys
import time
from ciscoisesdk import IdentityServicesEngineAPI
import ciscoisesdk

USAGE = """

Test ISE Python library.

Examples:
    ciscoisesdk_test.py 
    ciscoisesdk_test.py -i
    ciscoisesdk_test.py -itv

Requires setting the these environment variables using the `export` command:
    export IDENTITY_SERVICES_ENGINE_USERNAME=admin
    export IDENTITY_SERVICES_ENGINE_PASSWORD=ISEisC00L
    export IDENTITY_SERVICES_ENGINE_DEBUG=False
    export IDENTITY_SERVICES_ENGINE_BASE_URL='https://ise.domain.com'
    
You may add these export lines to a text file and load with `source`:
  source ise.sh

"""

def remove_ise_ids_and_links (resources:list=[]) :
    """
    Remove `id` and 'link' attributes to flatten ISE JSON data.
    """
    new_resources = []
    for r in resources:
        key, r = r.popitem() # unwrap ISE object name
        if type(r) == ciscoisesdk.models.mydict.MyDict :
            if r.get('id'): 
                del r['id']
            if r.get('link'): 
                del r['link']
        new_resources.append(r)
    return new_resources


def parse_cli_arguments () :
    """
    Parse the command line arguments
    """
    ARGS = argparse.ArgumentParser(
            description=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter,   # keep my format
            )
    ARGS.add_argument('-i', '--insecure', action='store_true', default=False, help='ignore cert checks')
    ARGS.add_argument('-t', '--timer', action='store_true', default=False, help='show response timer' )
    ARGS.add_argument('-v', '--verbose', action='store_true', default=False, help='Verbosity; multiple allowed')
    # ARGS.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    return ARGS.parse_args()


def main():
    """
    Entrypoint for packaged script.
    """

    global args     # promote to global scope for use in other functions
    args = parse_cli_arguments()

    # Load Environment Variables
    env = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }
    if args.verbose >= 3 : print(f'ⓘ env: {env}')
    if args.timer :
        global start_time
        start_time = time.time()

    ise = IdentityServicesEngineAPI(
            base_url=f"https://{env['ISE_HOSTNAME']}",  # IDENTITY_SERVICES_ENGINE_BASE_URL
            username=env['ISE_USERNAME'],               # IDENTITY_SERVICES_ENGINE_USERNAME
            password=env['ISE_PASSWORD'],               # IDENTITY_SERVICES_ENGINE_PASSWORD
            verify=(False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True)
          )

    sgts = ise.security_groups.get_security_groups()
    print(f"SGTs JSON:\n{json.dumps(sgts.response, indent=2)}", file=sys.stderr)

    sgts = sgts.response['SearchResult']['resources']
    print(f"SGT resources JSON:\n{json.dumps(sgts, indent=2)}", file=sys.stderr)

    sgt_ids = list(map(lambda x: x['id'], sgts))
    print(f"SGT IDs List:\n{sgt_ids}", file=sys.stderr)

    # Use the IDs to get all SGT details
    sgt_details = [ise.security_groups.get_security_group_by_id(id).response for id in sgt_ids ]
    sgt_details = remove_ise_ids_and_links(sgt_details)
    print(f"SGT Details:\n{sgt_details}", file=sys.stderr)

    nads = ise.network_device.get_all()
    print(f"NADS:\n{nads.response}", file=sys.stderr)

    if args.timer :
        duration = time.time() - start_time
        print(f'\n 🕒 {duration} seconds\n', file=sys.stderr)



if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    main()