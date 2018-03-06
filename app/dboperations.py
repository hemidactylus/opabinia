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
    dbAddRecordToTable,
    dbDeleteTable,
    dbCreateTable,
)

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

def dbGetRows(db,startDate=None, endDate=None):
    whereClause=prepareWhereClause('time',startDate,endDate)
    return dbRetrieveAllRecords(db,'counts',whereClause=whereClause)

def dbSaveRow(db, record):
    finalRecord={k :v for k,v in record.items()}
    now=datetime.utcnow()
    finalRecord['date']=now.date()
    finalRecord['time']=now
    dbAddRecordToTable(db,'counts',finalRecord)

def integrateRows(db, zeroDate=None, startDate=None, endDate=None):
    '''
        zeroDate is the left extreme of integration
        startDate is the first date to track in making the explicit list
        endDate is the end of the required time.

        Returned is an array of integrated values
        for all recorded ticks between startDate and endDate
    '''
    #
    print(startDate)
    whereClause=prepareWhereClause('time',zeroDate,endDate)
    #
    summedKeys={'count','abscount'}
    ini={k:0 for k in summedKeys}
    #
    rowCursor=dbRetrieveAllRecords(db,'counts',whereClause=whereClause)
    # traceless part (all the way to startDate)
    lastFound=None
    for doc in rowCursor:
        if doc['time']>=startDate:
            lastFound=doc
            break
        else:
            ini={
                k: ini[k]+doc[k]
                for k in summedKeys
            }
    #
    ini['time']=startDate
    results=[ini]
    if lastFound is not None:
        ini={
            k: ini[k]+lastFound[k]
            for k in summedKeys
        }
        ini['time']=lastFound['time']
        results.append(ini)
    # we have come to the traceful part
    for doc in rowCursor:
        ini={
            k: ini.get(k,0)+doc.get(k,0)
            for k in summedKeys
        }
        ini['time']=doc['time']
        results.append(ini)
    return results

def dbGetDateList(db):
    return sorted(
        tp[0]
        for tp in db.cursor().execute('SELECT DISTINCT(date) FROM counts;')
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
