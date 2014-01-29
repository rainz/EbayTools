import requests
import json
from sys import stdout

from Globals import *

def aspectRequest():
    categoryId = CPU_CATEGORY
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
        stdout.flush()
        allItems += items
        print "Retrieved " + str(retrieved) + " prices for page " + str(pageNo) + ". Total: " + str(len(allItems))
        pageNo += 1

