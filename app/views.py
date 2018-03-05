from time import time
import pytz

from flask import   (
    render_template,
    flash,
    redirect,
    session,
    url_for,
    request,
    g,
    send_file,
    send_from_directory,
)

from datetime import datetime, timedelta

from app import app

from config import (
    dbName,
    timeZone,
    recentnessTimeSpan,
    maxRecentItems,
    defaultHoursBack,
)

from dbtools import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbGetRows,
    dbSaveRow,
    integrateRows,
)

def localiseDate(dt):
    locDate=pytz.utc.localize(dt,is_dst=None)
    return locDate.astimezone(pytz.timezone(timeZone))

def localiseRow(row):
    nrow=row
    if nrow['time'] is not None:
        nrow['time']=localiseDate(row['time'])
    return nrow

# check at start
db=checkAndOpenDatabase(dbName)

def timeBounds(mode):
    now=datetime.utcnow()
    lastMidnight=datetime(*datetime.now().timetuple()[:3])
    if mode=='default':
        nHours=defaultHoursBack
        backTime=now-recentnessTimeSpan
    elif mode=='fullday':
        nHours=None
        backTime=lastMidnight
    else:
        try:
            nHours=abs(float(mode))
            if int(nHours)==nHours:
                nHours=int(nHours)
            backTime=now-timedelta(hours=nHours)
        except:
            nHours=defaultHoursBack
            backTime=now-recentnessTimeSpan
    return now,lastMidnight,backTime,nHours

@app.route('/')
@app.route('/index')
@app.route('/index/<mode>')
def ep_index(mode="default"):
    db=dbOpenDatabase(dbName)
    #
    now,lastMidnight,backTime,nH=timeBounds(mode)
    #
    entries=sorted(
        (
            localiseRow(row)
            for row in integrateRows(
                db,
                lastMidnight,
                backTime,
                now
            )
        ),
        key=lambda lRow: lRow['time'] if lRow['time'] is not None else localiseDate(datetime(1900,1,1)),
        reverse=True,
    )[:maxRecentItems]
    #
    hDesc='full day' if nH is None else 'last %s hours' % nH
    return render_template(
      "eventlist.html",
      text='Recent items (%s): %i' % (hDesc,len(entries)),
      pagetitle='Home',
      baseurl=url_for('ep_index'),
      pointlike=False, # three-col layout
      timespan=mode,
      entries=entries,
    )

@app.route('/events')
@app.route('/events/<mode>')
def ep_events(mode='default'):
    db=dbOpenDatabase(dbName)
    now,lastMidnight,backTime,nH=timeBounds(mode)
    entries=sorted(
        [
            locRow
            for locRow in (
                localiseRow(row)
                for row in dbGetRows(
                    db,
                    backTime,
                    now,
                )
            )
        ],
        key=lambda lRow: lRow['time'],
        reverse=True,
    )[:maxRecentItems]
    #
    hDesc='full day' if nH is None else 'last %s hours' % nH
    return render_template(
      "eventlist.html",
      text='Recent items (%s): %i' % (hDesc,len(entries)),
      pagetitle='Events',
      baseurl=url_for('ep_events'),
      pointlike=True, # this means: pointlike events, two-column layout
      timespan=mode,
      entries=entries,
    )

@app.route('/about')
def ep_about():
    return render_template(
        'about.html',
        pagetitle='About',
    )
