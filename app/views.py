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

from app.config import (
    dbName,
    timeZone,
    recentnessTimeSpan,
    maxRecentItems,
    defaultHoursBack,
)

from app.dboperations import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbGetRows,
    dbSaveRow,
    integrateRows,
    dbGetDateList,
)

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
    return nrow

def timeBounds(mode):
    now=datetime.utcnow()
    lastMidnight=findPreviousMidnight(now)
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
@app.route('/counters')
@app.route('/counters/<mode>')
@app.route('/index')
@app.route('/index/<mode>')
def ep_counters(mode='default'):
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
      "graphlist.html",
      text='Recent items (%s): %i' % (hDesc,len(entries)),
      pagetitle='Counts for %s' % (datetime.now().strftime('%B %d, %Y')),
      baseurl=url_for('ep_counters'),
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
      "graphlist.html",
      text='Recent items (%s): %i' % (hDesc,len(entries)),
      pagetitle='Events for %s' % (datetime.now().strftime('%B %d, %Y')),
      baseurl=url_for('ep_events'),
      pointlike=True, # this means: pointlike events, two-column layout
      timespan=mode,
      entries=entries,
    )

@app.route('/about')
def ep_about():
    return render_template(
        'about.html',
        pagetitle='About Opabinia',
    )

@app.route('/chooseday')
def ep_chooseday():
    db=dbOpenDatabase(dbName)
    return '\n'.join(
        str(d)
        for d in dbGetDateList(db)
    )
