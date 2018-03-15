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
    '''
        returns a (java)timestamp for a date
        safely beyond the provided one
        (used for the data endpoint for plotting)
    '''
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


def roundTime(dt, roundToSeconds):
   """
           Round a datetime object to any time laps in seconds
           dt : datetime.datetime object, default now.
           roundTo : Closest number of seconds to round to, default 1 minute.
           Author: Thierry Husson 2012 - Use it as you want but don't blame me.

            h/t "Le Droid" from https://stackoverflow.com/questions/3463930/
                                how-to-round-the-minute-of-a-datetime-object-python

   """
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundToSeconds/2) // roundToSeconds * roundToSeconds
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)

def timeHistogram(evtList,barSeconds):
    '''
        given a list of events with time and count=+/-1,
        a histogram of pairs of values is prepared
        along time, with a given quantisation
    '''
    maxTime=roundTime(
        max(ev['time'] for ev in evtList),
        barSeconds,
    )
    minTime=roundTime(
        min(ev['time'] for ev in evtList),
        barSeconds,
    )
    numDates=int((maxTime-minTime).total_seconds()/barSeconds)
    allDates=[
        minTime+timedelta(seconds=i*barSeconds)
        for i in range(numDates+1)
    ]
    histo={
        tDate : {
            'time': tDate,
            'jtimestamp': time.mktime(tDate.timetuple())*1000.0,
            'ins': 0,
            'outs': 0,
            'span': 1000.0*barSeconds,
        }
        for tDate in allDates
    }
    for evt in evtList:
        qDate=roundTime(evt['time'],barSeconds)
        if evt['count']>0:
            histo[qDate]['ins']+=1
        elif evt['count']<0:
            histo[qDate]['outs']+=1
    return sorted(
        histo.values(),
        key=lambda hData: hData['time']
    )
