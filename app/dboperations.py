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

from dateutils import (
    findPreviousMidnight,
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
    finalRecord['date']=now.date()
    finalRecord['time']=now
    dbAddRecordToTable(db,'counts',finalRecord)

def integrateRows(db, reqDate, cumulate=True):
    '''
        sorts and integrates (over time) the rows
        pertaining to the requested date, with
        a zero integration constant.

        if cumulate, the whole cumsum is returned;
        otherwise, only the final sum.

    '''
    #
    summedKeys={'count','abscount'}
    ini={k:0 for k in summedKeys}
    if cumulate:
        ini['time']=findPreviousMidnight(reqDate)
        results=[ini]
    else:
        maxFound=0
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
            maxFound=max(maxFound,ini['count'])
    if cumulate:
        return results
    else:
        result={k:v for k,v in ini.items()}
        result['max']=maxFound
        result['date']=reqDate
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
