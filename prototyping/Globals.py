from codecs import getwriter
from sys import argv, stdout

from ebaysdk import finding
from ebaysdk import shopping

MEM_CATEGORY = 170083
CPU_CATEGORY = 164
COMPUTER_PARTS_CATEGORY = 175673

UTF8Writer = getwriter('utf8')
stdout = UTF8Writer(stdout)

if len(argv) < 2:
  print "Please specify an Ebay app ID!"
  exit()

myAppId = argv[1]
apiFinding = finding(appid=myAppId)
apiShopping = shopping(appid=myAppId)
