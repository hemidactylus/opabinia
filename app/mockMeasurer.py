#!/usr/bin/python

'''
    Generation of mock passage data for testing
'''
from __future__ import print_function

from time import sleep
from random import random
import sys

from dbtools import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbSaveRow,
)
from config import (
    dbName
)

minTime=5
maxTime=10

if __name__=='__main__':

    db=checkAndOpenDatabase(dbName)
    print('Init mock measurer.')
    while True:
        tVal=-1 if random()<0.5 else +1
        print('*',end='')
        sys.stdout.flush()
        dbSaveRow(db,{'count':tVal,'abscount':abs(tVal)})
        db.commit()
        sleep(random()*(maxTime-minTime)+minTime)
