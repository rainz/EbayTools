from codecs import getwriter
from sys import argv, stdout

from ebaysdk import finding
from ebaysdk import shopping

import json
import os.path

home_dir = os.path.expanduser("~")

with open(os.path.join(home_dir, 'ApiKeys/EbayKey.json')) as key_file:    
    keys = json.load(key_file)

MEM_CATEGORY = 170083
CPU_CATEGORY = 164
COMPUTER_PARTS_CATEGORY = 175673

UTF8Writer = getwriter('utf8')
stdout = UTF8Writer(stdout)

myAppId = keys['AppId']
apiFinding = finding(appid=myAppId)
apiShopping = shopping(appid=myAppId)
