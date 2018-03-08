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
@app.route('/history/<daysback>')
def ep_history(daysback='7'):
    db=dbOpenDatabase(dbName)
    #
    if daysback!='forever':
        try:
            dbackInt=int(daysback)
            # to seek up to n days in the past,
            # we go back n-2 days: one because of the ">=" in the query,
            # one ... well I admit I have no idea but it seems to work. Damn trial-and-error,
            # damn dates.
            firstDate=findPreviousMidnight(datetime.utcnow())-timedelta(days=dbackInt-2)
        except:
            firstDate=None
    else:
        firstDate=None
    #
    print('FIRSTDATE %s' % str(firstDate))
    dates=dbGetDateList(db,startDate=firstDate)
    history={
        d: integrateRows(db,d,cumulate=False)
        for d in dates
    }
    return render_template(
        'history.html',
        pagetitle='History',
        text='History for Opabinia',
        history=history,
        daysback=daysback,
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
