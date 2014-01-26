#! /usr/bin/python

import requests
import lxml.html
from lxml import etree
import json
import codecs
import sys

from ebaysdk import finding
from ebaysdk import shopping

import StatUtil

myAppId = None

# memory=170083, cpu=164, computer parts=175673

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
                                    },
                                    {'name': 'BestOfferOnly',
                                     'value': 'true'
                                    }
                                   ],
                     'outputSelector': 'SellerInfo',
                     'sortOrder': 'EndTimeSoonest'
                    }
    if completed:
        op = 'findCompletedItems'
    else:
        op = 'findItemsAdvanced'

    apiFinding.execute(op, requestParams)

    dictResult = apiFinding.response_dict()
    
    # For debugging
    print json.dumps(dictResult)
    return
    
    if dictResult['ack']['value'] != 'Success':
        print "Request failed"
        return
        
    items = dictResult['searchResult']['item']
    for item in items:
        #pricing = item['sellingStatus']['currentPrice']['value'] + item['sellingStatus']['currentPrice']['currencyId']['value'] 
        itemPrice = item['sellingStatus']['convertedCurrentPrice']['value'];
        itemCurrency = item['sellingStatus']['convertedCurrentPrice']['currencyId']['value']
        pricing = itemPrice + itemCurrency
        try:
            shipping = item['shippingInfo']['shippingServiceCost']['value']
        except KeyError:
            shipping = '0'
        seller = item['sellerInfo']['sellerUserName']['value']
        totalCost = float(itemPrice) + float(shipping)
        print item['title']['value'], '|', item['condition']['conditionDisplayName']['value'], '|', pricing, '|', shipping, '|', seller # , '|', item['viewItemURL']['value']

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
    
    #apiFinding.execute('findItemsByCategory', requestParams)
    apiFinding.execute('findItemsAdvanced', requestParams)
    dictResult = apiFinding.response_dict()
    if dictResult['ack']['value'] != 'Success':
        print "Request failed"
        return  
    #print json.dumps(dictResult)
    return int(dictResult['paginationOutput']['totalEntries']['value'])

def getChildCategoriesRequest(categoryId):
    requestParams = {'CategoryID': str(categoryId),
                     'IncludeSelector': 'ChildCategories'
                    }
    apiShopping.execute('GetCategoryInfo', requestParams)
    dictResult = apiShopping.response_dict()
    if dictResult['Ack']['value'] != 'Success':
        print "Request failed"
        return

    #print json.dumps(dictResult)
    #return
    
    categories = dictResult['CategoryArray']['Category']
    if not isinstance(categories, list):
        catList = [categories] # probably a leaf node, no child categories
    else:
        catList = categories
    for c in catList:
        catId = int(c['CategoryID']['value'])
        if catId == categoryId:
            continue # don't print itself
        #totalCount = findCountInCategoryRequest(catId)
        print catId, c['CategoryName']['value'], c['LeafCategory']['value'], #totalCount

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
    
def priceAnalysis():
    categoryId = 164
    entriesPerPage = 10
    pageNo = 1
    completed = True
    keywords = ['Q9400 -mod -adapter']
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': ' '.join(keywords),
                     'outputSelector': 'SellerInfo',
                     'sortOrder': 'EndTimeSoonest'
                    }
    if completed:
        op = 'findCompletedItems'
    else:
        op = 'findItemsAdvanced'

    prices = []
    totalPages = 1
    while pageNo <= totalPages:
        requestParams['paginationInput']['pageNumber'] = str(pageNo)
        apiFinding.execute(op, requestParams)
        dictResult = apiFinding.response_dict()
        
        # For debugging
        #print json.dumps(dictResult)
        #return
        
        if dictResult['ack']['value'] != 'Success':
            print "Request failed for page", pageNo
            break
        
        totalPages = int(dictResult['paginationOutput']['totalPages']['value'])
        items = dictResult['searchResult']['item']
        retrieved = len(items)
        if retrieved == 0:
            break
        print "Retrieved " + str(retrieved) + " prices for page " + str(pageNo)
        sys.stdout.flush()
        for item in items:
            #pricing = item['sellingStatus']['currentPrice']['value'] + item['sellingStatus']['currentPrice']['currencyId']['value'] 
            itemPrice = item['sellingStatus']['convertedCurrentPrice']['value'];
            itemCurrency = item['sellingStatus']['convertedCurrentPrice']['currencyId']['value']
            pricing = itemPrice + itemCurrency
            try:
                shipping = item['shippingInfo']['shippingServiceCost']['value']
            except KeyError:
                shipping = '0'
            seller = item['sellerInfo']['sellerUserName']['value']
            totalCost = float(itemPrice) + float(shipping)
            prices.append(totalCost)
        pageNo += 1
        
    print "Total price count:", len(prices)
    print prices
    f = StatUtil.filterOutliers(prices)
    print f

def getCompletedForCategory(categoryId):
    entriesPerPage = 200
    pageNo = 1
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }
                    }
    
    op = 'findItemsByCategory'
    totalPages = 1
    allItems = []
    while pageNo <= totalPages:
        requestParams['paginationInput']['pageNumber'] = str(pageNo)
        apiFinding.execute(op, requestParams)
        dictResult = apiFinding.response_dict()
        
        # For debugging
        #print json.dumps(dictResult)
        #return
        
        if dictResult['ack']['value'] != 'Success':
            print "Request failed for page", pageNo
            break
        
        totalPages = int(dictResult['paginationOutput']['totalPages']['value'])
        items = dictResult['searchResult']['item']
        retrieved = len(items)
        if retrieved == 0:
            break
        sys.stdout.flush()
        allItems += items
        print "Retrieved " + str(retrieved) + " prices for page " + str(pageNo) + ". Total: " + str(len(allItems))
        pageNo += 1
    
if len(sys.argv) < 2:
  print "Please provide an Ebay app ID!"
  exit()

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

myAppId = sys.argv[1]
apiFinding = finding(appid=myAppId)
apiShopping = shopping(appid=myAppId)

#aspectRequest()
findAdvancedRequest(True)
#getPopular(164)
#print findCountInCategoryRequest(170083)
#priceAnalysis()
#getCompletedForCategory(164)