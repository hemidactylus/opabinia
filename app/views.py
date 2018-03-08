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
    dateFormat,
    niceDateFormat,
)

from app.dboperations import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbGetRows,
    dbSaveRow,
    integrateRows,
    dbGetDateList,
)

from dateutils import (
    findPreviousMidnight,
    localiseDate,
    localiseRow,
    timeBounds,
    normaliseReqDate,
    monthNames,
)

from dictutils import makeDateListToTree

@app.route('/')
@app.route('/counters')
@app.route('/counters/<date>')
def ep_counters(date='today'):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    entries=sorted(
        [
            localiseRow(row)
            for row in integrateRows(
                db,
                queryDate,
            )
        ],
        key=lambda evt: evt['time'],
        reverse=True,
    )
    reqdate=normaliseReqDate(date)
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetitle='Counts for %s' % (queryDate.strftime(niceDateFormat)),
      baseurl=url_for('ep_counters'),
      twocolumns=False, # three-col layout
      reqdate=reqdate,
      entries=entries,
      cdtarget='counters',
    )

@app.route('/events')
@app.route('/events/<date>')
def ep_events(date='today'):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    entries=sorted(
        [
            locRow
            for locRow in (
                localiseRow(row)
                for row in dbGetRows(
                    db,
                    queryDate
                )
            )
        ],
        key=lambda evt: evt['time'],
        reverse=True,
    )
    #
    reqdate=normaliseReqDate(date)
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetitle='Hits for %s' % (queryDate.strftime(niceDateFormat)),
      baseurl=url_for('ep_events'),
      twocolumns=True, # this means: pointlike events, two-column layout
      reqdate=reqdate,
      entries=entries,
      cdtarget='events',
    )

@app.route('/history')
def ep_history():
    db=dbOpenDatabase(dbName)
    dates=dbGetDateList(db)
    history={
        d: integrateRows(db,d,cumulate=False)
        for d in dates
    }
    return render_template(
        'history.html',
        history=history
    )

@app.route('/about')
def ep_about():
    return render_template(
        'about.html',
        pagetitle='About Opabinia',
    )

@app.route('/chooseday')
@app.route('/chooseday/<target>')
def ep_chooseday(target='counters'):
    db=dbOpenDatabase(dbName)
    dates=dbGetDateList(db)
    dateTree=makeDateListToTree(dates)

    # these are the names of the endpoint functions!
    epname={
        'counters': 'ep_counters',
        'events': 'ep_events',
    }.get(target,'ep_counters')
    eptitle={
        'counters': 'Counts',
        'events': 'Hits',
    }.get(target,'Counts')

    return render_template(
        'chooseday.html',
        pagetitle='Select the date for %s' % eptitle,
        datetree=dateTree,
        epname=epname,
        monthnames=monthNames,
    )
