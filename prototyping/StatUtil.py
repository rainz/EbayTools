from numpy import average
from numpy import median
from numpy import std

def _filterHelper(vals):
    avg = average(vals)
    med = median(vals)
    stdev = std(vals)
    
    lower = avg - 2*stdev
    upper = avg + 2*stdev
    
    return [x for x in vals if x >= lower and x <= upper]
    
def filterOutliers(vals):
    f1 = _filterHelper(vals)
    return _filterHelper(f1)
    
def _unitTest():
    prices = [92, 9, 14, 99, 103, 142, 900, 121, 119, 100, 89, 96, 105, 108, 115, 109, 96]
    print prices
    f1 = _filterHelper(prices)
    print f1
    f2 = _filterHelper(f1)
    print f2
