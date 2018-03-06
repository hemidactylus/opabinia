'''
  dbtools.py
'''

import sqlite3 as lite
import os
import stat
from operator import itemgetter
from datetime import datetime

from dbschema import dbTablesDesc

DB_DEBUG=False

sqlDateFormat='%Y-%m-%d %H:%M:%S'

def listColumns(tableName):
    '''
        reads the table structure and returns an *ordered*
        list of its fields
    '''
    colList=[]
    if 'primary_key' in dbTablesDesc[tableName]:
        colList+=map(itemgetter(0),dbTablesDesc[tableName]['primary_key'])
    colList+=map(itemgetter(0),dbTablesDesc[tableName]['columns'])
    return colList

def dbAddRecordToTable(db,tableName,recordDict):
    colList=listColumns(tableName)
    #
    insertStatement='INSERT INTO %s VALUES (%s)' % (tableName, ', '.join(['?']*len(colList)))
    insertValues=tuple(recordDict[k] for k in colList)
    #
    if DB_DEBUG:
        print('[dbAddRecordToTable] %s' % insertStatement)
        print('[dbAddRecordToTable] %s' % ','.join('%s' % iv for iv in insertValues))
    db.execute(insertStatement, insertValues)
    #
    return

def dbUpdateRecordOnTable(db,tableName,newDict, allowPartial=False):
    dbKeys=list(map(itemgetter(0),dbTablesDesc[tableName]['primary_key']))
    otherFields=list(map(itemgetter(0),dbTablesDesc[tableName]['columns']))
    updatePart=', '.join('%s=?' % of for of in otherFields if not allowPartial or of in newDict)
    updatePartValues=[newDict[of] for of in otherFields if not allowPartial or of in newDict]
    whereClause=' AND '.join('%s=?' % dbk for dbk in dbKeys)
    whereValues=[newDict[dbk] for dbk in dbKeys]
    updateStatement='UPDATE %s SET %s WHERE %s' % (tableName,updatePart,whereClause)
    updateValues=updatePartValues+whereValues
    if DB_DEBUG:
        print('[dbUpdateRecordOnTable] %s' % updateStatement)
        print('[dbUpdateRecordOnTable] %s' % ','.join('%s' % iv for iv in updateValues))
    db.execute(updateStatement, updateValues)
    #
    return

def dbOpenDatabase(dbFileName):
    con = lite.connect(dbFileName,detect_types=lite.PARSE_DECLTYPES)
    return con

def dbDeleteTable(db,tableName):
    '''
        caution: this DROPS a table without further questions
    '''
    deleteCommand='DROP TABLE %s;' % tableName
    if DB_DEBUG:
        print('[dbDeleteTable] %s' % deleteCommand)
    cur=db.cursor()
    cur.execute(deleteCommand)

def dbCreateTable(db,tableName,tableDesc):
    '''
        tableName is a string
        tableDesc can contain a 'primary_key' -> nonempty array of pairs  (name,type)
                    and holds a 'columns'     -> similar array with other (name,type) items
    '''
    fieldLines=[
        '%s %s' % fPair
        for fPair in list(tableDesc.get('primary_key',[]))+list(tableDesc['columns'])
    ]
    createCommand='CREATE TABLE %s (\n\t%s\n);' % (
        tableName,
        ',\n\t'.join(
            fieldLines+(
                ['PRIMARY KEY (%s)' % (', '.join(map(itemgetter(0),tableDesc['primary_key'])))]
                if 'primary_key' in tableDesc else []
            )
        )
    )
    if DB_DEBUG:
        print('[dbCreateTable] %s' % createCommand)
    cur=db.cursor()
    cur.execute(createCommand)
    # if one or more indices are specified, create them
    if 'indices' in tableDesc:
        '''
            Syntax for creating indices:
                CREATE INDEX index_name ON table_name (column [ASC/DESC], column [ASC/DESC],...)
        '''
        for indName,indFieldPairs in tableDesc['indices'].items():
            createCommand='CREATE INDEX %s ON %s ( %s );' % (
                indName,
                tableName,
                ' , '.join('%s %s' % fPair for fPair in indFieldPairs)
            )
        if DB_DEBUG:
            print('[dbCreateTable] %s' % createCommand)
        cur=db.cursor()
        cur.execute(createCommand)

def dbClearTable(db, tableName):
    '''
        deletes *ALL* entries from a table. Careful!
    '''
    cur=db.cursor()
    deleteStatement='DELETE FROM %s' % tableName
    if DB_DEBUG:
        print('[dbClearTable] %s' % deleteStatement)
    cur.execute(deleteStatement)

def prepareWhereClause(fieldName,startDate=None,endDate=None):
    whereClauses=[]
    if startDate is not None:
        whereClauses.append('%s > \'%s\''  % (fieldName,startDate.strftime(sqlDateFormat)))
    if endDate is not None:
        whereClauses.append('%s <= \'%s\'' % (fieldName,endDate.strftime(sqlDateFormat)))
    if len(whereClauses):
        whereClause='WHERE %s ' % ' AND '.join(whereClauses)
    else:
        whereClause=' '
    return whereClause

def dbRetrieveAllRecords(db, tableName, whereClause=None):
    '''
        returns an iterator on dicts,
        one for each item in the table,
        in no particular order AT THE MOMENT
    '''
    cur=db.cursor()
    selectStatement='SELECT * FROM %s%s' % (tableName,'' if whereClause is None else ' %s' % whereClause)
    if DB_DEBUG:
        print('[dbRetrieveAllRecords] %s' % selectStatement)
    cur.execute(selectStatement)
    for recTuple in cur.fetchall():
        yield dict(zip(listColumns(tableName),recTuple))

def dbRetrieveRecordsByKey(db, tableName, keys, whereClauses=[]):
    '''
        keys is for instance {'id': '123', 'status': 'm'}
    '''
    cur=db.cursor()
    kNames,kValues=zip(*list(keys.items()))
    fullWhereClauses=['%s=?' % kn for kn in kNames] + whereClauses
    whereClause=' AND '.join(fullWhereClauses)
    selectStatement='SELECT * FROM %s WHERE %s' % (tableName,whereClause)
    if DB_DEBUG:
        print('[dbRetrieveRecordsByKey] %s' % selectStatement)
        print('[dbRetrieveRecordsByKey] %s' % ','.join('%s' % iv for iv in kValues))
    cur.execute(selectStatement, kValues)
    docTupleList=cur.fetchall()
    if docTupleList is not None:
        return ( dict(zip(listColumns(tableName),docT)) for docT in docTupleList)
    else:
        return None

def dbRetrieveRecordByKey(db, tableName, key):
    '''
        key is for instance {'id': '123'}
        and specifies the primary key of the table.
        Converts to dict!
    '''
    cur=db.cursor()
    kNames,kValues=zip(*list(key.items()))
    whereClause=' AND '.join('%s=?' % kn for kn in kNames)
    selectStatement='SELECT * FROM %s WHERE %s' % (tableName,whereClause)
    if DB_DEBUG:
        print('[dbRetrieveRecordByKey] %s' % selectStatement)
        print('[dbRetrieveRecordByKey] %s' % ','.join('%s' % iv for iv in kValues))
    cur.execute(selectStatement, kValues)
    docTuple=cur.fetchone()
    if docTuple is not None:
        docDict=dict(zip(listColumns(tableName),docTuple))
        return docDict
    else:
        return None

def dbDeleteRecordsByKey(db, tableName, key):
    cur=db.cursor()
    kNames,kValues=zip(*list(key.items()))
    whereClause=' AND '.join('%s=?' % kn for kn in kNames)
    deleteStatement='DELETE FROM %s WHERE %s' % (tableName, whereClause)
    if DB_DEBUG:
        print('[dbDeleteRecordsByKey] %s' % deleteStatement)
        print('[dbDeleteRecordsByKey] %s' % ','.join('%s' % iv for iv in kValues))
    cur.execute(deleteStatement, kValues)

## SPECIALIZATIONS

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
    finalRecord['time']=datetime.utcnow()
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
