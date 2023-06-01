#!/usr/bin/env python3
"""
ise_sdk_test.py

Author: Thomas Howard, thomas@cisco.com
"""

import argparse
import requests
import json
import os
import sys
import time
from ciscoisesdk import IdentityServicesEngineAPI

USAGE = """

Test ISE Python library.

Examples:
    ise_sdk_test.py 
    ise_sdk_test.py -v
    ise_sdk_test.py -vvv

Requires setting the these environment variables using the `export` command:
    export IDENTITY_SERVICES_ENGINE_USERNAME=admin
    export IDENTITY_SERVICES_ENGINE_PASSWORD=ISEisC00L
    export IDENTITY_SERVICES_ENGINE_DEBUG=False
    export IDENTITY_SERVICES_ENGINE_BASE_URL='https://ise.domain.com'
    
You may add these export lines to a text file and load with `source`:
  source ise.sh

"""

def parse_cli_arguments () :
    """
    Parse the command line arguments
    """
    ARGS = argparse.ArgumentParser(
            description=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter,   # keep my format
            )
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
            base_url=f"https://{env['ISE_HOSTNAME']}",
            username=env['ISE_USERNAME'],
            password=env['ISE_PASSWORD'],
          )

    sgts = ise.security_groups.get_security_groups()
    print(json.dumps(sgts.response, indent=2))
    sgts = sgts.response['SearchResult']['resources']
    print(sgts)
    uuids = list(map(lambda x: x['id'], sgts))
    print(uuids)
    responses = [ise.security_groups.get_security_group_by_id(uuid).response for uuid in uuids ]
    print(responses)

    
    nads = ise.network_device.get_all()
    print(nads.response)

    if args.timer :
        duration = time.time() - start_time
        print(f'\n 🕒 {duration} seconds\n', file=sys.stderr)



if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    main()