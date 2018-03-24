'''
    api.py : the primitives behind the data/view queries
'''

import time
from datetime import datetime

from app.config import (
    dbName,
    barSeconds,
)

from dateutils import (
    timeBounds,
    sortAndLocalise,
    timeHistogram,
)

from app.dboperations import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbGetRows,
    dbSaveRow,
    integrateRows,
    dbGetDateList,
)

def getEvents(date):
    '''
        all events for a given date (possibly None->today)
    '''
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    entries=sortAndLocalise(
        dbGetRows(
            db,
            queryDate
        )
    )
    histo=timeHistogram(entries,barSeconds=barSeconds)
    return {
        'data': histo,
        'now': time.mktime((datetime.now()).timetuple())*1000.0,
    }


def getCounters(date):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    dataPoints=sortAndLocalise(
        integrateRows(
            db,
            queryDate,
        )
    )
    return {
        'data': dataPoints,
        'now': time.mktime(datetime.utcnow().timetuple())*1000.0,
    }

def jHistorizer(hItem):
    '''
        provides a histogram item with a jtimestamp
    '''
    nDict={
        k: hItem[k]
        for k in hItem.keys()#['count','ins','abscount','max']
    }
    nDict['jtimestamp']=time.mktime(hItem['date'].timetuple())*1000.0
    return nDict

def getHistory(daysback):
    db=dbOpenDatabase(dbName)
    if daysback!='forever':
        try:
            dbackInt=int(daysback)
            firstDate=findPreviousMidnight(datetime.utcnow())-timedelta(days=dbackInt-2)
        except:
            firstDate=None
    else:
        firstDate=None
    dates=dbGetDateList(db,startDate=firstDate)
    history=[
        jHistorizer(integrateRows(db,d,cumulate=False))
        for d in sorted(dates)
    ]
    return {
        'data': history,
        'now': time.mktime((datetime.now()).timetuple())*1000.0,
    }
