#! /usr/bin/python

import requests
import lxml.html
from lxml import etree

from pymongo import MongoClient
from pymongo import errors

import codecs
import sys

def populateTable(db, collName, targetUrl, tableId):
    print "%s: retrieving data from %s" % (collName, targetUrl)
    f = requests.get(targetUrl)
    doc = lxml.html.fromstring(f.text)

    # Get column headers
    table = doc.xpath('//table[@id="'+tableId+'"]')[0];
    titleNodes = table.xpath('thead/tr/th');
    titles = []
    for t in titleNodes:
      titleStr = t.text
      if titleStr == None:
        titleStr = t.xpath('div')[0].text
      titles.append(titleStr)
    numCols = len(titles)
    
    # Store all values in a list
    tableData = []
    for idx, row in enumerate(table.xpath('tbody/tr')):
      cells = row.xpath('td')
      if len(cells) != numCols:
        continue
      rowData = {}
      for idx in range(numCols):
        cellData = cells[idx].text
        if cellData == None:
          cellData = cells[idx].xpath('a')[0].text
        rowData[titles[idx]] = cellData
      tableData.append(rowData)
    
    print "%s: %d entries retrieved. Key field is '%s'. Updating db..." % (collName, len(tableData), titles[0])
    if len(tableData) < 3:
      print "Too few entries in the table. Not updating db!"
      return
    
    # Insert all values into DB table
    collection = db[collName]
    collection.remove() # clear table
    collection.insert(tableData) # bulk insert
    #for row in tableData:
        #collection.insert(row)
    collection.ensure_index(titles[0])
    
    print "%s: done updating db" % collName
    
def main():
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)

    try:
        if len(sys.argv) < 3:
            mongoClient = MongoClient() # connect to local db if no credentials are given
        else:
            dbUser = sys.argv[1]
            dbPass = sys.argv[2]
            mongoURI = "mongodb://%s:%s@linus.mongohq.com:10059/PCBenchmarks" % (dbUser, dbPass)
            print "Connecting to %s..." % mongoURI
            mongoClient = MongoClient(mongoURI)
    except errors.ConnectionFailure:
      print "Cannot connect to db!"
      exit()

    dbBench = mongoClient.PCBenchmarks
    populateTable(dbBench, 'VideoCard', 'http://www.videocardbenchmark.net/gpu_list.php', 'cputable')
    populateTable(dbBench, 'SingleCPU', 'http://www.cpubenchmark.net/cpu_list.php', 'cputable')
    populateTable(dbBench, 'MultiCPU', 'http://www.cpubenchmark.net/cpu_list.php', 'multicpu')

    mongoClient.disconnect()
    
main()
