import requests
import lxml.html
from lxml import etree

from Globals import *

def dict2xml(paramDict, root):
    for key, value in paramDict.iteritems():
        child = etree.SubElement(root, key)
        if (isinstance(value, dict)):
            dict2xml(value, child)
        else:
            child.text = value
            
def postRequestXml():
    targetUrl = 'http://svcs.ebay.com/services/search/FindingService/v1'
    headers = {'X-EBAY-SOA-SERVICE-NAME': 'FindingService',
               'X-EBAY-SOA-OPERATION-NAME': 'findItemsAdvanced',
               'X-EBAY-SOA-SERVICE-VERSION': '1.12.0',
               'X-EBAY-SOA-GLOBAL-ID': 'EBAY-US',
               'X-EBAY-SOA-SECURITY-APPNAME': 'YuZhaob4f-960c-4aed-b5da-7dcf6d18ede',
               'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'XML'
              }
    ebayOpName = 'findItemsAdvanced'
    xmlnsUrl = 'http://www.ebay.com/marketplace/search/v1/services'
    categoryId = CPU_CATEGORY
    entriesPerPage = 10
    pageNo = 2
    keywords = ['(Q9450, Q9400) -adapter']
    requestRoot = etree.Element(ebayOpName+"Request", xmlns=xmlnsUrl)
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': ' '.join(keywords),
                     'sortOrder': 'EndTimeSoonest'
                    }
    dict2xml(requestParams, requestRoot)

    response = requests.post(targetUrl, data=etree.tostring(requestRoot), headers=headers)
    print response.text
    #doc = lxml.html.fromstring(response.text)

postRequestXml()
