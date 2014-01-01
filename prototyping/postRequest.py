#! /usr/bin/python

import requests
import lxml.html
from lxml import etree

import json

from ebaysdk import finding
from ebaysdk import shopping

import codecs
import sys

myAppId = None

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
    categoryId = 164
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
    
# To do: try itemFilter, aspectFilter, and outputSelector
def findAdvancedRequest(completed=False):
    categoryId = 164
    entriesPerPage = 20
    pageNo = 1
    #keywords = ['(Q9450, Q9400) -adapter']
    keywords = ['intel', 'i5']
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': ' '.join(keywords),
                     'aspectFilter': [{'aspectName': 'Number of Cores',
                                      'aspectValueName' : '2'
                                      },
                                      {'aspectName': 'Clock Speed',
                                       'aspectValueName' : '2.5 GHz - 2.99 GHz'
                                      }
                                     ],
                     'itemFilter': [{'name': 'Condition',
                                     'value': ['New', '2000']
                                    }
                                   ],
                     'sortOrder': 'EndTimeSoonest'
                    }
    if completed:
        op = 'findCompletedItems'
    else:
        op = 'findItemsAdvanced'

    apiFinding.execute(op, requestParams)

    dictResult = apiFinding.response_dict()
    #print json.dumps(dictResult)
    #return
    if dictResult['ack']['value'] != 'Success':
        print "Request failed"
        return
        
    items = dictResult['searchResult']['item']
    for item in items:
        #pricing = item['sellingStatus']['currentPrice']['value'] + item['sellingStatus']['currentPrice']['currencyId']['value'] 
        pricing = item['sellingStatus']['convertedCurrentPrice']['value'] + item['sellingStatus']['convertedCurrentPrice']['currencyId']['value']
        shipping = item['shippingInfo']['shippingServiceCost']['value']
        print item['title']['value'], '|', item['condition']['conditionDisplayName']['value'], '|', pricing, '|', shipping # , '|', item['viewItemURL']['value']

def aspectRequest():
    categoryId = 164
    entriesPerPage = 2
    pageNo = 1
    keywords = ['Intel']
    requestParams = {'categoryId': str(categoryId),
                     'outputSelector': 'AspectHistogram',
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': ' '.join(keywords),
                     'sortOrder': 'EndTimeSoonest'
                    }

    apiFinding.execute('findItemsAdvanced', requestParams)
    dictResult = apiFinding.response_dict()
    if dictResult['ack']['value'] != 'Success':
        print "Request failed"
        return

    aspects = dictResult['aspectHistogramContainer']['aspect']
    for asp in aspects:
        print asp['name']['value']
        for aspVal in asp['valueHistogram']:
            print "    " + aspVal['valueName']['value']
    
    #print json.dumps(apiFinding.response_dict())
    
def findCountInCategoryRequest(categoryId):
    entriesPerPage = 20
    pageNo = 1
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }
                    }
    
    apiFinding.execute('findItemsByCategory', requestParams)
    dictResult = apiFinding.response_dict()
    if dictResult['ack']['value'] != 'Success':
        print "Request failed"
        return  
    #print json.dumps(dictResult)
    return int(dictResult['paginationOutput']['totalEntries']['value'])

def getCategoriesRequest(categoryId):
    requestParams = {'CategoryID': str(categoryId),
                     'IncludeSelector': 'ChildCategories'
                    }
    apiShopping.execute('GetCategoryInfo', requestParams)
    dictResult = apiShopping.response_dict()
    if dictResult['Ack']['value'] != 'Success':
        print "Request failed"
        return

    #print json.dumps(dictResult)
    categories = dictResult['CategoryArray']['Category']
    for c in categories:
        catId = int(c['CategoryID']['value'])
        if catId == categoryId:
            continue
        totalCount = findCountInCategoryRequest(catId)
        print catId, c['CategoryName']['value'], c['LeafCategory']['value'], totalCount

def getPopular(categoryId):
    maxEntries = 5
    requestParams = {'CategoryID': str(categoryId),
                     'MaxEntries': str(maxEntries),
                     'QueryKeywords': 'Intel i5'
                    }
    apiShopping.execute('FindPopularItems', requestParams)
    dictResult = apiShopping.response_dict()
    if apiShopping.error():
        print "An error has occurred!"
        return
    if dictResult['Ack']['value'] != 'Success':
        print "Request failed"
        return
    print json.dumps(dictResult)
    

        
if len(sys.argv) < 2:
  print "Please provide an Ebay app ID!"
  exit()

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

myAppId = sys.argv[1]
apiFinding = finding(appid=myAppId)
apiShopping = shopping(appid=myAppId)

#aspectRequest()
#findAdvancedRequest()
getPopular(164)