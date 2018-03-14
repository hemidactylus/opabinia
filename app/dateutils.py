'''
    dateutils.py : various date manipulation
    (including timezone hell)
'''

import pytz
from datetime import datetime, timedelta
import time

from config import (
    timeZone,
    dateFormat,
    niceDateFormat,
)

monthNames=[
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
]

def findPreviousMidnight(naiveDT):
    '''
        given a naive date, returns the utc date
        of the most recent midnight (for that timezone,
        but recast as utc)

        Somehow this seems to work, but damn timezones!
    '''
    locMidnight = pytz \
        .timezone(timeZone) \
        .localize(datetime(*localiseDate(naiveDT).timetuple()[:3]))
    return datetime(*locMidnight.utctimetuple()[:5])

def localiseDate(dt):
    locDate=pytz.utc.localize(dt,is_dst=None)
    return locDate.astimezone(pytz.timezone(timeZone))

def localiseRow(row):
    nrow=row
    if nrow['time'] is not None:
        nrow['time']=localiseDate(row['time'])
        nrow['jtimestamp']=time.mktime(nrow['time'].timetuple())*1000.0
    return nrow
def jtimestampLatest(dpoints):
    latest=max(dpoints,key=lambda dp: dp['time'])['time']
    locNow=localiseDate(datetime.now())
    if latest+timedelta(hours=1) > locNow:
        finalpoint=locNow
    else:
        finalpoint=latest+timedelta(hours=1)
    return time.mktime((finalpoint).timetuple())*1000.0

def timeBounds(datename):
    '''
        given a datename, i.e.
            '2017-03-23'
        or
            'today', 'yesterday'
        two things are returned:
        the date and the previous midnight, both
        as utc datetimes
    '''
    if datename=='today':
        reqDate=datetime(*localiseDate(datetime.utcnow()).date().timetuple()[:3]) #datetime.utcnow()
        print(reqDate)
    elif datename=='yesterday':
        reqDate=datetime(*localiseDate(datetime.utcnow()-timedelta(days=1)).date().timetuple()[:3])
    else:
        try:
            reqDate=datetime.strptime(datename,dateFormat)
        except:
            reqDate=datetime.utcnow()
    #
    lastMidnight=findPreviousMidnight(reqDate)
    return reqDate,lastMidnight

def normaliseReqDate(rdate):
    '''
        when possible brings the date string
        to a name, for setting the active buttons
        in the web page
    '''
    for possibleName in ['today','yesterday']:
        if rdate==possibleName or timeBounds(possibleName)[0].strftime(dateFormat)==rdate:
          return possibleName
    return rdate

def sortAndLocalise(evtList):
    return sorted(
        (
            localiseRow(evt)
            for evt in evtList
        ),
        key=lambda evt: evt['time'],
        reverse=True,
    )
