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
    jsonify,
)

from datetime import datetime, timedelta

from app import app

from app.config import (
    dbName,
    timeZone,
    dateFormat,
    niceDateFormat,
    fileNameDateFormat,
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
    sortAndLocalise,
    jtimestampLatest,
)

from dictutils import makeDateListToTree

from spreadsheets import makeSpreadsheet

@app.route('/')
@app.route('/counters')
@app.route('/counters/<date>')
def ep_counters(date='today'):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    entries=sortAndLocalise(
        integrateRows(
            db,
            queryDate,
        )
    )
    reqdate=normaliseReqDate(date)
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetype='Counts',
      pagetitle='Counts',
      baseurl=url_for('ep_counters'),
      queryDate=queryDate,
      twocolumns=False, # three-col layout
      reqdate=reqdate,
      entries=entries,
      cdtarget='counters',
      niceDateFormat=niceDateFormat,
    )

@app.route('/datacounters')
@app.route('/datacounters/<date>')
def ep_datacounters(date='today'):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    dataPoints=sortAndLocalise(
        integrateRows(
            db,
            queryDate,
        )
    )
    return jsonify(
        {
            'points': dataPoints,
            'now': jtimestampLatest(dataPoints),
        }
    )

@app.route('/events')
@app.route('/events/<date>')
def ep_events(date='today'):
    db=dbOpenDatabase(dbName)
    queryDate,lastMidnight=timeBounds(date)
    entries=sortAndLocalise(
        dbGetRows(
            db,
            queryDate
        )
    )
    reqdate=normaliseReqDate(date)
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetype='Hits',
      pagetitle='Hits',
      baseurl=url_for('ep_events'),
      twocolumns=True, # this means: pointlike events, two-column layout
      reqdate=reqdate,
      queryDate=queryDate,
      entries=entries,
      cdtarget='events',
      niceDateFormat=niceDateFormat,
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
    dates=dbGetDateList(db,startDate=firstDate)
    history={
        d: integrateRows(db,d,cumulate=False)
        for d in dates
    }
    return render_template(
        'history.html',
        pagetitle='History',
        history=history,
        daysback=daysback,
        dateFormat=dateFormat,
        niceDateFormat=niceDateFormat,
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
        dateFormat=dateFormat,
    )

@app.route('/download_history')
def ep_download_history():
    db=dbOpenDatabase(dbName)
    now=localiseDate(datetime.utcnow())
    # 1. history
    dates=dbGetDateList(db,startDate=None)
    history={
        d: integrateRows(db,d,cumulate=False)
        for d in dates
    }
    # 2. daily detail
    dates=dbGetDateList(db)
    perDay={
        tDate: sortAndLocalise(
            integrateRows(
                db,
                datetime(*tDate.timetuple()[:3]),
            )
        )
        for tDate in dates
    }
    #
    spreadsheet = makeSpreadsheet(history=history,perDay=perDay,now=now)
    #
    spreadsheetFilename='opabinia_history_%s.xlsx' % now.strftime(fileNameDateFormat)
    return send_file (
        spreadsheet,
        attachment_filename=spreadsheetFilename,
        as_attachment=True,
        last_modified=now,
        cache_timeout=0,
    )
