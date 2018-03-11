'''
    dboperations.py : higher-level stuff built on top of the dbtools
'''

import os
import stat
from datetime import datetime, date

from dbtools import (
    dbOpenDatabase,
    prepareWhereClause,
    dbRetrieveAllRecords,
    dbRetrieveRecordByKey,
    dbAddRecordToTable,
    dbDeleteTable,
    dbCreateTable,
)

from dateutils import (
    findPreviousMidnight,
    localiseDate,
)

from config import dateFormat

from dbschema import dbTablesDesc

def setRWAttributeForAll(filename):
    '''
        Set rw-rw-rw attribute to database file
    '''
    attrConstant=stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    os.chmod(filename, attrConstant )

def checkAndOpenDatabase(dbName):
    if not os.path.isfile(dbName):
        print('[checkAndOpenDatabase] Going to create DB "%s"!' % dbName)
        db=dbOpenDatabase(dbName)
        for tName, tContents in dbTablesDesc.items():
            try:
                retVal=dbDeleteTable(db, tName)
            except:
                pass
            retVal=dbCreateTable(db, tName, tContents)
        db.commit()
        setRWAttributeForAll(dbName)
        print('Done.')
    return dbOpenDatabase(dbName)

def dbGetRows(db,reqDate):
    whereClause='date = \'%s\'' % reqDate.strftime(dateFormat)
    return dbRetrieveAllRecords(db,'counts',whereClause=whereClause)

def dbSaveRow(db, record):
    finalRecord={k :v for k,v in record.items()}
    now=datetime.utcnow()
    finalRecord['date']=localiseDate(now).date()
    finalRecord['time']=now
    dbAddRecordToTable(db,'counts',finalRecord)

def dbSaveHistory(db, record):
    '''
        the history item should be completely done by this time
    '''
    dbAddRecordToTable(db,'history',record)

def dbGetHistory(db, date):
    return dbRetrieveRecordByKey(db,'history',date)

def integrateRows(db, reqDate, cumulate=True):
    '''
        sorts and integrates (over time) the rows
        pertaining to the requested date, with
        a zero integration constant.

        if cumulate, the whole cumsum is returned;
        otherwise, only the final sum.

        * upon a cumulate=false call, a day that is old enough
          can be cached for speedy lookup later.

    '''
    #
    summedKeys={'count','abscount'}
    ini={k:0 for k in summedKeys}
    if cumulate:
        ini['time']=findPreviousMidnight(reqDate)
        results=[ini]
    else:
        # check if on cache
        cacheable=reqDate < localiseDate(datetime.utcnow()).date()
        if cacheable:
            cachedDoc=dbGetHistory(db,{'date':reqDate})
            if cachedDoc is not None:
                return cachedDoc
        #
        maxFound=0
        insFound=0
    #
    whereClause='date = \'%s\'' % reqDate.strftime(dateFormat)
    rowCursor=dbRetrieveAllRecords(db,'counts',whereClause=whereClause)
    #
    for doc in rowCursor:
        ini={
            k: ini.get(k,0)+doc.get(k,0)
            for k in summedKeys
        }
        if cumulate:
            ini['time']=doc['time']
            results.append(ini)
        else:
            insFound=insFound+(1 if ini['count']>0 else 0)
            maxFound=max(maxFound,ini['count'])
    if cumulate:
        return results
    else:
        result={k:v for k,v in ini.items()}
        result['max']=maxFound
        result['ins']=insFound
        result['date']=reqDate
        # cache to 'history' if old enough
        if cacheable:
            dbSaveHistory(db,result)
            db.commit() # it would be nice to move this to a datelist-level!
        #
        return result

def dbGetDateList(db,startDate=None):
    #
    if startDate is not None:
        whereClause='date >= \'%s\'' % startDate.strftime(dateFormat)
    else:
        whereClause=None
    #
    return sorted(
        tp[0]
        for tp in db.cursor().execute(
            'SELECT DISTINCT(date) FROM counts %s;' % (
                ''
                if whereClause is None
                else ' WHERE %s' % whereClause
            )
        )
    )

if __name__=='__main__':
    from config import dbName
    from datetime import datetime

    db=checkAndOpenDatabase(dbName)
    print('\n'.join(map(str,integrateRows(
        db,
        zeroDate=datetime(2018,3,4,12,58),
        startDate=datetime(2018,3,4,13,39),
        endDate=datetime(2018,3,4,13,50),
    ))))
