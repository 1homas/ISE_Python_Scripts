#!/usr/bin/env python3
"""
Get the total number of a specific ISE ERS resource.
See https://cs.co/ise-api for REST API resource names.

Usage: ise-ers-count.py {resource_name}

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import requests
import os
import sys


# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()


"""
Return the number of resources of type resource.
"""
def ise_ers_resource_count (resource) :
    count = 0
    r = requests.get(f"https://{ENV['ISE_PPAN']}/ers/config/{resource_name}",
                     auth=(ENV['ISE_REST_USERNAME'], ENV['ISE_REST_PASSWORD']),
                     headers={'Accept': 'application/json'},
                     verify=ENV['ISE_CERT_VERIFY'].lower().startswith('t')
                    )
    if r.status_code == 200 :
        count = r.json()['SearchResult']['total']
    elif r.status_code == 404 :
        print(f'{r.status_code} Unknown resource: {resource}', file=sys.stderr)
    else :
        print(f'{r.status_code} uh oh {r.text}', file=sys.stderr)
    return count



"""
__main__
"""
if __name__ == "__main__":
    """
    Entrypoint for local script.
    """

    # Load Environment Variables
    ENV = { k : v for (k, v) in os.environ.items() }

    if len(sys.argv) <= 1 :
        print('❌ Missing resource name', file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1) # not OK
    resource_name = sys.argv[1]

    count = ise_ers_resource_count(resource_name)
    print(count)
    sys.exit(0) # 0 == OK

