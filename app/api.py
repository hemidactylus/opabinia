'''
    api.py : the primitives behind the data/view queries
'''

import time
from datetime import datetime, timedelta

from app.config import (
    dbName,
    barSeconds,
)

from dateutils import (
    timeBounds,
    sortAndLocalise,
    timeHistogram,
    findPreviousMidnight,
    javaTimestamp,
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
        'now': javaTimestamp(datetime.now()),
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
        'now': javaTimestamp(datetime.now()),
    }

def jHistorizer(hItem):
    '''
        provides a histogram item with a jtimestamp
    '''
    nDict={
        k: hItem[k]
        for k in hItem.keys()#['count','ins','abscount','max']
    }
    nDict['jtimestamp']=javaTimestamp(hItem['date'])
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
        for d in sorted(dates,reverse=True)
    ]
    return {
        'data': history,
        'now': javaTimestamp(datetime.now()),
    }

def getCurrentStatus(now):
    db=dbOpenDatabase(dbName)
    curStatus=integrateRows(db,now.date(),cumulate=False)
    return curStatus
