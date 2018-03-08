'''
    dictutils.py : various utilities to handle dictionaries
'''

def convertIterableToDictOfLists(iterable, keyer, valuer):
    '''
        Given an iterable, and a keyer and valuer function,
        a map key -> list of items is returned
    '''
    dictionary={}
    for item in iterable:
        key=keyer(item)
        if key not in dictionary:
            dictionary[key]=[valuer(item)]
        else:
            dictionary[key].append(valuer(item))
    return dictionary

def sortAndMarkDates(dlist):
    '''
        sort a list of Dates and also marks them as weekend or not,
        embedding them into a dict format made for the choose-date template
    '''
    return [
        {'date': date, 'weekday': date.weekday() in {0,1,2,3,4}}
        for date in sorted(dlist)
    ]

def makeDateListToTree(datelist):
    '''
        Makes a list of dates into a tree
            year -> month -> (sorted) date list
    '''
    return {
        yr: {
            mth: sortAndMarkDates(mlist)
            for mth, mlist in convertIterableToDictOfLists(
                ylist,
                keyer=lambda d: d.month,
                valuer=lambda d:d,
            ).iteritems()
        }
        for yr, ylist in convertIterableToDictOfLists(
            datelist,
            keyer=lambda d: d.year,
            valuer=lambda d:d,
        ).iteritems()
    }
