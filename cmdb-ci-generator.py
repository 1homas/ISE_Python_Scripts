#!/usr/bin/env python3
"""
Generate configuration management database (CMDB) configuration items (CIs).

Examples:
    cmdb_ci_generator.py
    cmdb_ci_generator.py --help
    cmdb_ci_generator.py -v > CMDB.json
    cmdb_ci_generator.py -n 1000 
    cmdb_ci_generator.py -f pretty -tvn 1_000_000 > CMDB_1M.json
"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import argparse
import csv
import json
import yaml
import io
import os.path              # for local file cache
import random
import requests             # for downloading OUIs
import re
from faker import Faker     # generate fake users, MACs, IPs
import collections
import pandas as pd         # dataframes
import sys
import time


ITEM_COUNT = 1                  # default number of config items to generate
PARENT_OBJECT_NAME = 'table'    # Parent Object Name for JSON & YAML output

#
# 💡 Un/comment locations or create your own as needed
# 
THEATERS = ['AMER','EMEA','APJC']
REGIONS = [f"Region {i}" for i in range(1,10)]
ZONES = [f"Zone {i}" for i in range(1,10)]
LOCATIONS = '''
Region,  Country,   City3,  CityName,           Building
AMER,    CA,        VAN,    Vancouver,          01
AMER,    CA,        TTO,    Toronto,            01
AMER,    BR,        RDJ,    Rio de Janero,      01
AMER,    BR,        SAO,    Sao Paulo,          01
AMER,    MX,        MXC,    Mexico City,        01
AMER,    US,        AST,    Austin,             01
AMER,    US,        ATL,    Atlanta,            01
AMER,    US,        CHI,    Chicago,            01
AMER,    US,        HBC,    Huntington Beach,   01
AMER,    US,        HRN,    Herndon,            01
AMER,    US,        IRV,    Irvine,             01
AMER,    US,        NYC,    New York,           01
AMER,    US,        RCD,    Richardson,         01
AMER,    US,        RTP,    Raleigh,            01
AMER,    US,        SJC,    San Jose,           01
AMER,    US,        SJC,    San Jose,           02
AMER,    US,        SJC,    San Jose,           03
AMER,    US,        SJC,    San Jose,           04
AMER,    US,        SJC,    San Jose,           05
AMER,    US,        SJC,    San Jose,           06
AMER,    US,        SJC,    San Jose,           07
AMER,    US,        SJC,    San Jose,           08
AMER,    US,        SJC,    San Jose,           09
AMER,    US,        SJC,    San Jose,           10
APJC,    AU,        SYD,    Sydney,             01
APJC,    IN,        BGL,    Bengaluru,          01
APJC,    JP,        TYO,    Tokyo,              01
APJC,    KR,        SEO,    Seoul,              01
APJC,    SG,        SIN,    Singapore,          01
EMEA,    CZ,        PRG,    Prague,             01
EMEA,    DE,        BER,    Berlin,             01
EMEA,    FR,        PRS,    Paris,              01
EMEA,    IT,        MLN,    Milan,              01
EMEA,    NL,        AMS,    Amsterdam,          01
EMEA,    SA,        JBG,    Johannesburg,       01
EMEA,    UA,        DUB,    Dubai,              01
EMEA,    UK,        LON,    London,             01
'''

HOSPITAL_DEPARTMENTS_CSV = '''
Name
Accounts
Administration
Admitting
Bacteriology
Biochemistry
BloodBank
BusinessManagement
Cardiology
Dental
Dietary
EarNoseThroat
Gynecology
Hematology
Housekeeping
InfectiousDisease
Inpatient
Laundry
Maintenance
Mechanical
Neurology
Nuclear
Nursing
Obstetrics
Opthamology
Orthopedics
Outpatient
Paramedical
Parasitology
Pastoral
Pathology
Pediatrics
Personnel
Pharmacy
Psychiatry
Purchasing
Radiology
Reconstruction
Records
Rehabilitation
Serology
Skin
SocialServices
Sterilization
Supplies
Surgery
Waste
'''

UNIVERSITY_DEPARTMENTS_CSV = '''
Abbr,Name
AAG,Anthropology and Geography
AER,Aerospace
AGB,Agricultural Business
AGR,Agriculture
AGS,Agricultural Science
ARC,Architecture
ARE,Architectural Engineering
ART,Art and Design
ASC,Animal Science
BIO,Biochemistry
BM,Biomedical
BSC,Biological Sciences
BUS,Business
CE,Civil Engineering
CES,Comparative Ethnic Studies
CHM,Chemistry
CM,Construction Management
CON,Construction
CPE,Computer Engineering
CRP,City and Regional Planning
CS,Computer Science
ECN,Economics
EE,Electrical Engineering
EGR,Engineering
ENG,English
ES,Ethnic Studies
FS,Food Science
GE,General Engineering
HIS,History
IE,Industrial Engineering
IT,Industrial Technology
JRN,Journalism
KIN,Kinesiology
LA,Landscape Architecture
LAN,Languages
LS,Liberal Studies
MAN,Manufacturing Engineering
MAT,Materials Engineering
MB,Microbiology
ME,Mechanical Engineering
MS,Marine Sciences
MSC,Music
MTH,Mathematics
NRM,Natural Resources Management
NUT,Nutrition
NVE,Environmental Engineering
NVS,Environmental Sciences
PH,Public Health
PHL,Philosophy
PHY,Physics
PLS,Plant Sciences
POL,Political Science
PSY,Psychology
REC,Recreation Administration
SCI,Science
SOC,Sociology
STS,Statistics
SWE,Software Engineering
TA,Theatre Arts
VIT,Viticulture
'''

#
# 💡 Un/comment the general endpoint types to use
#
ENDPOINT_GROUPS = '''
Name,               Description
#--- Classifications
# Allowed,            Allowed
# Blocked,            Blocked
# Assets,             Assets
# Retired,            Retired
# Expired,            Expired
#--- General IT
# IOT,                IOT
Computer,           Computer
Mobile,             Mobile
Desktops,           Desktops
Laptops,            Laptops
Raspberry_Pi,       Raspberry Pi
Printers,           Printers
Phones,             Phones
Servers,            Servers
Smartphones,        Smartphones
Tablets,            Tablets
Telepresence,       Webex
Workstations,       Workstations
VoIP,               A voice-over-IP phone
#--- Lab
AP,                 Access Point
Lab,                Lab
Power,              "Power Supplies, Outlets, UPS, etc."
RFID,               RFID Sensors
UPS,                Uninterruptible Power Supply (UPS)
#--- Building & Facilities
Badge_Readers,      Badge Readers
Cameras,            Cameras
Facilities,         Facilities
Lighting,           Lighting
HVAC,               HVAC
Elevators,          Elevators
Pumps,              Pumps
Signage,            Signage
Thermostats,        Thermostats
Vending,            Vending
#--- Entertainment
Entertainment,      Entertainment
Amazon_Echo,        AmazonTV
Amazon_TV,          AmazonTV
Amazon_FireStick,   Amazon_FireStick
Apple_TV,           Apple TV
Apple_iPad,         Apple iPad
Roku,               Roku
TV,                 Television (any manufacturer)
game_console,       Video game console like the Xbox or PlayStation
media_device,       "audiovisual equipment, music players, audio systems, TVs, and projectors"
#--- Manufacturing
Manufacturing,      Manufacturing
PLC,                PLC
Robot,              Robot
Painting,           Painting
Assembly,           Assembly
#--- Medical
Medical,            Medical
#--- Retail
PoS,                Point of Sale
Register,           Register
Scanner,            Scanner
'''

#
# 💡 Un/comment the general endpoint types to use or add your own
#
OSes = '''
Type,       Vendor,         Name,       Version
RHEL,       Red Hat,        RHEL,       6.x
RHEL,       Red Hat,        RHEL,       7.x
RHEL,       Red Hat,        RHEL,       8.x
Linux,      Ubuntu,         Ubuntu,     22.04
Linux,      Ubuntu,         Ubuntu,     22.10
Linux,      Ubuntu,         Ubuntu,     23.04
Windows,    Microsoft,      Windows,    XP
Windows,    Microsoft,      Windows,    7
Windows,    Microsoft,      Windows,    8
Windows,    Microsoft,      Windows,    10
Windows,    Microsoft,      Windows,    11
macOS,      Apple,          macOS,      13.1
macOS,      Apple,          macOS,      13.2
macOS,      Apple,          macOS,      13.3
Android,    Google,         Android,    9
Android,    Google,         Android,    10
Android,    Google,         Android,    11
Android,    Google,         Android,    12
Android,    Google,         Android,    13
Android,    Google,         Android,    14
Android,    Google,         Android,    15
iOS,        Apple,          iOS,        14.x
iOS,        Apple,          iOS,        15.x
iOS,        Apple,          iOS,        16.x
'''


#
# 💡 Un/comment the general endpoint types to use or add your own
#
CORPORATE_DEPARTMENTS = [
    'Finance',
    'HR',
    'IT',
    'Management',
    'Marketing',
    'Product',
    'Sales',
    'Services',
    'Vendors',
]

OPERATIONAL_STATUS = [
    'Operational',        # In or ready for use
    'Non-operational',    # The opposite of operational
    'Repair-In-Progress', # It is being fixed
    'Standby',            # For DR purposes
    'Ready',              # Configured and ready to be deployed
    'Retired',            # previously used, and now withdrawn (maybe you now just steal parts from it)\
    'Quarantine',
]


faker = Faker('en-US')    # fake data generator
username_cache = {}       # NAS identifier name cache to ensure uniqueness


def get_username (firstname=faker.first_name(), lastname=faker.last_name()) :
    """
    Returns the next available instance (name-#) of a name
    """
    # print(f"get_username({firstname},{lastname})")
    n = 1
    username = (firstname[0:1] + lastname[0:8]).lower()
    while (username in username_cache) :
        # print('❌ Collision!')
        n += 1
        username = (firstname[0:1] + lastname[0:8] + str(n)).lower()

    username_cache[username] = 1    # cache it
    return username


def generate_cmdb_ci_6_columns (count=1) :
    """
    6 attributes
    """
    items = []
    for record in range(1,count+1) :

        location = (df_locations.sample())
        os = df_oses.sample()

        items.append( { 
            'MAC' : faker.mac_address().upper(),
            'Hardware-Type' : df_endpoint_groups.sample().iloc[0]['Name'],
            'iPSK' : faker.password(12),
            'Operational-Status' : random.choice(OPERATIONAL_STATUS),
            'Created' : faker.past_datetime(start_date='-5y').isoformat(sep='T'),
            'Updated' : faker.past_datetime(start_date='-6m').isoformat(sep='T'),
        } )

    return items # list of dicts 


def generate_cmdb_ci (count=1) :
    """
    """
    items = []
    for record in range(1,count+1) :

        firstname = faker.first_name()
        lastname = faker.last_name()
        username = get_username(firstname, lastname)
        location = (df_locations.sample())  # choose a singe location at random
        os = df_oses.sample()
        network_type = random.choice(['wired','wireless'])

        items.append( { 
            'Inventory-Id' : faker.uuid4(),
            'Name' : faker.hostname(1).split('.',maxsplit=1)[0],
            'Description' : faker.sentence(nb_words=8),
            'Operational-Status' : random.choice(OPERATIONAL_STATUS),
            'Created' : faker.past_datetime(start_date='-5y').isoformat(sep='T'),
            'Updated' : faker.past_datetime(start_date='-6m').isoformat(sep='T'),

            # hardware
            'Hardware-Type' : df_endpoint_groups.sample().iloc[0]['Name'],

            # software
            'OS' : os.iloc[0]['Name'],
            'OS-Version' : os.iloc[0]['Version'],

            # organizational
            'Owner-First-Name' : firstname,
            'Owner-Last-Name' : lastname,
            'Owner_Email' : username,
            'Department' : random.choice(CORPORATE_DEPARTMENTS),
            'Zone' : random.choice(ZONES),

            # network ienformation
            'Network_Type' : network_type,
            'iPSK' : faker.password(12) if (network_type == 'wireless' and os.iloc[0].Type in ['RHEL','Linux']) else '',
            'MAC' : faker.mac_address().upper(),
            'Endpoint-IPv4-Static' : faker.ipv4_private() if faker.boolean(.1) else '',
            'Identity-Group' : 'Employee',

            # network authorization
            'Authorization' : random.choice(['Internet','Employee','Quarantine','Guest','IOT']),

            # location information
            'Site' : location.iloc[0]['City3'],
            'Building' : location.iloc[0]['Building'],
            'Floor' : '',   # not implemented
            'Room' : '',   # not implemented
        } )
    if args.verbosity >= 3: print(f"ⓘ  items() :\n{items}", file=sys.stderr)

    return items # list of dicts 


def load_IEEE_OUIs () :
    """
    Return a DataFrame of IEEE OUIs, downloading the data from the IEEE, if necessary.
    """
    IEEE_OUI_URL = 'https://standards-oui.ieee.org/oui/oui.txt'
    IEEE_OUI_FILENAME = IEEE_OUI_URL.split('/')[-1]
    IEEE_OUI_CSV_FILENAME = 'oui.csv'
    if args.verbosity : print(f"ⓘ load_IEEE_OUIs() ...", file=sys.stderr)

    # Download IEEE OUIs locally for conversion to CSV if we do not have it
    if (not os.path.exists(IEEE_OUI_FILENAME)) :
        if args.verbosity : print(f"ⓘ   requests Fetching: {IEEE_OUI_URL}", file=sys.stderr)
        try:
            response = requests.get(IEEE_OUI_URL)
            with open(IEEE_OUI_FILENAME, 'w') as file: file.write(response.text)
            print(f"ⓘ   {IEEE_OUI_FILENAME} saved")
        except requests.exceptions.ConnectionError:
            print("You've got problems with connection.", file=sys.stderr)

    # Parse IEEE OUIs for only the "base 16" lines
    if (not os.path.exists(IEEE_OUI_CSV_FILENAME)) :
        if args.verbosity : print(f"ⓘ   Parsing base16 IEEE OUIs ...", file=sys.stderr)
        with open(IEEE_OUI_FILENAME, 'r') as file: 
            lines = file.readlines()
            oui_table = [['OUI','Organization']]  # list of lists for CSV file
            for line in lines :
                if (re.search('(base 16)', line)) :
                    oui,org = re.split('\s+\(base 16\)\s+', line)
                    oui_table.append([oui, org.strip()])

        # Save filtered oui_table to CSV file
        with open(IEEE_OUI_CSV_FILENAME, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(oui_table)
            print(f"ⓘ   {IEEE_OUI_CSV_FILENAME} saved")

    # Read OUIs into DataFrame
    if (os.path.exists(IEEE_OUI_CSV_FILENAME)) :
        if args.verbosity : print(f"ⓘ   Reading cached CSV of IEEE OUIs", file=sys.stderr)
        return pd.read_csv(IEEE_OUI_CSV_FILENAME)
        



def load_dataframes () :
    """
    Return a DataFrame of IEEE OUIs, downloading the data from the IEEE, if necessary.
    """
    if args.verbosity : print(f"ⓘ load_dataframes()", file=sys.stderr)

    # Load Locations
    global df_locations
    df_locations = pd.read_csv( io.StringIO(LOCATIONS), comment='#', skipinitialspace=True)
    # 💡 Cast Building numbers to object/text to prevent numpy from using int64 type which is not supported by JSON! 
    df_locations['Building'] = df_locations['Building'].astype("object")
    # print(f"City3 values: {df_locations.City3.values}")
    # print(f"AMER City3 values: {df_locations[df_locations.Region.str.startswith('AMER')].City3.values}")
    # print(f"AJPC City3 values: {df_locations[df_locations.Region.str.startswith('APJC')].City3.values}")
    # print(f"EMEA City3 values: {df_locations[df_locations.Region.str.startswith('EMEA')].City3.values}")

    #
    # 💡 IEEE OUI data is not used but could be for generating specific vendors!
    #
    # Load OUIs
    # global df_ouis
    # df_ouis = load_IEEE_OUIs()
    # print(f"ⓘ   IEEE OUIs: {len(df_ouis)}")
    # print(f"ⓘ   - Cisco OUIs: {len(df_ouis[df_ouis.Organization.str.contains('Cisco')])}")
    # print(f"ⓘ   - Meraki OUIs: {len(df_ouis[df_ouis.Organization.str.contains('Meraki')])}")
    # print(f"ⓘ   -  Orgs:\n{df_ouis.Organization.value_counts()}")
    # print(f"ⓘ   Cisco OUIs: {df_ouis[df_ouis.Organization.str.contains('Cisco')]['OUI'].tolist()}")
    # print(f"ⓘ   get_ouis_by_org('cisco'): {get_ouis_by_org('cisco')}")

    global df_oses
    df_oses = pd.read_csv(io.StringIO(OSes), comment='#', skipinitialspace=True)
    # print(f"df_oses: {df_oses}")

    global df_endpoint_groups
    df_endpoint_groups = pd.read_csv(io.StringIO(ENDPOINT_GROUPS), comment='#', skipinitialspace=True )
    # print(f"ⓘ - Endpoint Groups: {len(df_endpoint_groups)}\n{df_endpoint_groups}")

    global df_hospital_departments
    df_hospital_departments = pd.read_csv(io.StringIO(HOSPITAL_DEPARTMENTS_CSV), comment='#', skipinitialspace=True)
    # print(f"df_hospital_departments: {df_hospital_departments.Name}")
    # print(f"Hospital Department: {df_hospital_departments.iloc(random.randint(0,len(df_hospital_departments)).strip()}")

    global df_university_departments
    df_university_departments = pd.read_csv(io.StringIO(UNIVERSITY_DEPARTMENTS_CSV), comment='#', skipinitialspace=True)
    # print(len(df_university_departments))
    # print(f"df_university_departments: {df_university_departments.Name}")
    # print(f"University Department: {df_university_departments[random.randint(0,len(df_university_departments))]['Name'].strip()}")


def get_ouis_by_org (org:str=None) :
    """
    Returns a list of OUIs containing the org string in the organization field.
    """
    return df_ouis[df_ouis.Organization.str.lower().str.contains(org.lower())]['OUI'].tolist()


def show (resources=None, resource_name=None, format='pretty', filename='-') :
    """
    Shows the resources in the specified format to the file handle.

    @resources : the list of dictionary items to format
    @resource_name : the name of the resource. Example: endpoint, sgt, etc.
    @format    : 
        - `csv`   : Show the items in a Comma-Separated Value (CSV) format
        - `grid`  : Show the items to a grid/table
        - `json`  : Show the items as a single JSON string
        - `line`  : Show the items as JSON with each item on it's own line
        - `pretty`: Show the items as JSON pretty-printed with 2-space indents
        - `yaml`  : Show the items as YAML with 2-space indents
    @filename  : Default: `sys.stdout`
    """
    if resources == None : return
    
    if args.verbosity : print(f"ⓘ show(): {len(resources)} resources of type {type(resources[0])} as {format}", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened
    fh = sys.stdout # write to terminal by default
    if filename != '-' :
        if args.verbosity : print(f"ⓘ Opening {filename}", file=sys.stderr)
        fh = open(filename, 'w')

    if format == 'csv':  # CSV
        headers = {}
        [headers.update(r) for r in resources]  # find all unique keys
        writer = csv.DictWriter(fh, headers.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in resources:
            writer.writerow(row)

    elif format == 'grid':  # grid
        print(f"{tabulate(resources, headers='keys', tablefmt='simple_grid')}", file=fh)

    elif format == 'line':  # JSON, 1 line per object
        print('{')
        print(f'"{resource_name}" = [')
        [print(json.dumps(r), end=',\n', file=fh) for r in resources]
        print(']\n}')

    elif format == 'json':  # JSON, one long string
        print(json.dumps({ resource_name : resources }), file=fh)

    elif format == 'pretty':  # pretty-print
        print(json.dumps({ resource_name : resources }, indent=2), file=fh)

    elif format == 'yaml':  # YAML
        print(yaml.dump({ resource_name : resources }, indent=2, default_flow_style=False), file=fh)

    else:  # just in case something gets through the CLI parser
        print(f' 🛑 Unknown format: {format}', file=sys.stderr)


def main():
    """
    Entrypoint for script.
    """
    global args     # promote to global scope for use in other functions
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter) # Keep __doc__ format
    argp.add_argument('--filename', default='-', required=False, help='Save output to filename. Default: stdout')
    argp.add_argument('-n', '--number', type=int, default=ITEM_COUNT, help='Number of config items to generate')
    argp.add_argument('-f', '--format', choices=['csv', 'grid', 'json', 'line', 'pretty', 'yaml'], default='pretty')
    argp.add_argument('-t', '--timer', action='store_true', default=False, help='show response timer' )
    argp.add_argument('-v', '--verbosity', action='count', default=0, help='Verbosity; multiple allowed')
    args = argp.parse_args()

    if args.verbosity >= 3 : print(f"ⓘ Args: {args}")
    if args.verbosity : print(f"ⓘ filename: {'- (stdout)' if args.filename == '-' else args.filename}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ format: {args.format}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ number: {args.number}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ timer: {args.timer}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ verbosity: {args.verbosity}", file=sys.stderr)

    if args.timer :
        global start_time
        start_time = time.time()

    # load PINs, Locations, NADs, Users, Protocols into DataFrames
    if args.verbosity : print(f"ⓘ Loading DataFrames ...", file=sys.stderr)
    load_dataframes()

    if args.verbosity : print(f"ⓘ Generating: {args.number} items ...", file=sys.stderr)
    items = generate_cmdb_ci(args.number)
    # items = generate_cmdb_ci_6_columns(args.number)

    if args.verbosity : print(f"ⓘ Total Config Items = {len(items)}", file=sys.stderr)

    show(items, PARENT_OBJECT_NAME, args.format, args.filename)

    if args.timer :
        duration = time.time() - start_time
        print(f"🕒 {duration} seconds\n", file=sys.stderr)


if __name__ == '__main__':
    """
    Runs main() if file wasn't imported.  
    """
    main()
