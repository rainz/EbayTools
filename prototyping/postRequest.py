import requests
import json
from sys import stdout

from Globals import *
from Category import *
from StatUtil import *

def findAdvancedRequest(completed=False):
    categoryId = CPU_CATEGORY
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
                                    },
                                    {'name': 'LocatedIn',
                                     'value': 'US'
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

def getResults(categoryId, searchStr, auction=True, buyItNow=False, bestOffer=False, soldItems=False):
    entriesPerPage = 50
    pageNo = 1
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': searchStr,
                     'itemFilter': [{'name': 'Condition',
                                     'value': ['1000',
                                               '1500',
                                               '1750',
                                               '2000',
                                               '2500',
                                               '3000',
                                               '4000',
                                               '5000',
                                               '6000']
                                    },
                                    {'name': 'LocatedIn',
                                     'value': 'US'
                                    },
                                   ],
                     'outputSelector': 'SellerInfo',
                     'sortOrder': 'EndTimeSoonest'
                    }
    if soldItems:
        op = 'findCompletedItems'
        requestParams['itemFilter'].append({'name': 'SoldItemsOnly',
                                             'value': 'true'
                                           })
    else:
        op = 'findItemsAdvanced'

    listTypes = []
    if auction:
        listTypes.append('Auction')

    if buyItNow:
        listTypes.extend(['AuctionWithBIN', 'FixedPrice', 'StoreInventory'])
    requestParams['itemFilter'].append({'name': 'ListingType',
                                        'value': listTypes, 
                                       })
    if bestOffer:
        requestParams['itemFilter'].append({'name': 'BestOfferOnly',
                                            'value': 'true'
                                           })

    totalPages = 1
    allItems = []
    while pageNo <= totalPages:
        requestParams['paginationInput']['pageNumber'] = str(pageNo)
        apiFinding.execute(op, requestParams)
        dictResult = apiFinding.response_dict()
        
        if dictResult['ack']['value'] != 'Success':
            print "Request failed for page", pageNo
            break
        
        totalPages = int(dictResult['paginationOutput']['totalPages']['value'])
        items = dictResult['searchResult']['item']
        retrieved = len(items)
        if retrieved == 0:
            break
        allItems.extend(items)
        #print "Retrieved " + str(retrieved) + " prices for page " + str(pageNo)
        stdout.flush()
        pageNo += 1

    return allItems

def testGetResults():
    results = getResults(CPU_CATEGORY, 'q9400 -771', True, True, False, True)
    for item in results:
        sellingState = item['sellingStatus']['sellingState']['value']
        country = item['country']['value']
        condition = item['condition']['conditionDisplayName']['value']
        pricing = item['sellingStatus']['currentPrice']['value'] + item['sellingStatus']['currentPrice']['currencyId']['value']
        listingType = item['listingInfo']['listingType']['value']
        print '|'.join([country, condition, pricing, listingType, sellingState])
    #print "Total: " + str(len(results))

def priceAnalysis():
    categoryId = CPU_CATEGORY
    entriesPerPage = 50
    pageNo = 1
    completed = True
    searchStr = ['Q9400 -771']
    #searchStr = ['i7']
    buyItNow = False
    requestParams = {'categoryId': str(categoryId),
                     'paginationInput': {'entriesPerPage': str(entriesPerPage),
                                         'pageNumber': str(pageNo)
                                        }, 
                     'keywords': searchStr,
                     'itemFilter': [{'name': 'Condition',
                                     'value': ['1000',
                                               '1500',
                                               '1750',
                                               '2000',
                                               '2500',
                                               '3000',
                                               '4000',
                                               '5000',
                                               '6000']
                                    },
                                    {'name': 'LocatedIn',
                                     'value': 'US'
                                    },
                                    {'name': 'SoldItemsOnly',
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
    if buyItNow:
        requestParams['itemFilter'].append({'name': 'ListingType',
                                            'value': ['AuctionWithBIN', 
                                                      'FixedPrice',
                                                      'StoreInventory']
                                           })
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
        stdout.flush()
        for item in items:
            #sellingState = item['sellingStatus']['sellingState']['value']
            #if sellingState != 'EndedWithSales':
            #    print sellingState
            #    continue
            #country = item['country']['value']
            #if country != 'US':
            #    print "Non-US:", country
            #    continue
            #condition = item['condition']['conditionId']['value']
            #if condition == "7000":
            #    print item['condition']['conditionDisplayName']['value']
            #pricing = item['sellingStatus']['currentPrice']['value'] + item['sellingStatus']['currentPrice']['currencyId']['value']
            #listingType = item['listingInfo']['listingType']['value']
            #if not listingType in ['AuctionWithBIN', 'FixedPrice', 'StoreInventory']:
            #    print listingType, item['viewItemURL']['value']
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
    f = filterOutliers(prices)
    print f

#aspectRequest()
#findAdvancedRequest(True)
#getPopular(CPU_CATEGORY)
#print findCountInCategoryRequest(MEM_CATEGORY)
#getCompletedForCategory(CPU_CATEGORY)
#priceAnalysis()
testGetResults()
