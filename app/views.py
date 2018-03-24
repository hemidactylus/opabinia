import time
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
    barSeconds,
)

from app.dboperations import (
    dbOpenDatabase,
    dbGetRows,
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
    roundTime,
    timeHistogram,
)

from api import (
    getEvents,
    getCounters,
    getHistory,
    getCurrentStatus,
)

from dictutils import makeDateListToTree

from spreadsheets import makeSpreadsheet

@app.route('/')
@app.route('/index')
def ep_index():
    dNow=datetime.now()
    curStatus=getCurrentStatus(dNow)
    print(curStatus)
    #
    return render_template(
        "index.html",
        data=curStatus,
        niceDateFormat=niceDateFormat,
        now=dNow,
        pagetype='Index',
    )

@app.route('/counters')
@app.route('/counters/<date>')
def ep_counters(date='today'):
    entries=getCounters(date)
    reqDate=normaliseReqDate(date)
    reqUrl=url_for('ep_datacounters',date=reqDate)
    queryDate,lastMidnight=timeBounds(date)
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries['data'])),
      pagetype='Counts',
      pagetitle='Counts',
      baseurl=url_for('ep_counters'),
      reqUrl=reqUrl,
      queryDate=queryDate,
      reqDate=reqDate,
      entries=entries,
      cdtarget='counters',
      niceDateFormat=niceDateFormat,
    )

@app.route('/datacounters')
@app.route('/datacounters/<date>')
def ep_datacounters(date='today'):
    return jsonify(getCounters(date))

@app.route('/events')
@app.route('/events/<date>')
def ep_events(date='today'):
    queryDate,lastMidnight=timeBounds(date)
    histo=getEvents(date)
    reqDate=normaliseReqDate(date)
    reqUrl=url_for('ep_dataevents',date=reqDate)
    return render_template(
      "graphlist.html",
      text='(each bar spans %.2f minutes)' % (barSeconds/60.0),
      pagetype='Hits',
      pagetitle='Flux',
      baseurl=url_for('ep_events'),
      reqUrl=reqUrl,
      reqDate=reqDate,
      queryDate=queryDate,
      entries=histo,
      cdtarget='events',
      niceDateFormat=niceDateFormat,
    )

@app.route('/dataevents')
@app.route('/dataevents/<date>')
def ep_dataevents(date='today'):
    return jsonify(getEvents(date))

@app.route('/history')
@app.route('/history/<daysback>')
def ep_history(daysback='7'):
    history=getHistory(daysback)
    reqUrl=url_for('ep_datahistory',daysback=daysback)
    return render_template(
        'history.html',
        pagetitle='History',
        history=history,
        daysback=daysback,
        dateFormat=dateFormat,
        niceDateFormat=niceDateFormat,
        daysBack=daysback,
        pagetype='History',
        reqUrl=reqUrl,
    )

@app.route('/datahistory')
@app.route('/datahistory/<daysback>')
def ep_datahistory(daysback='7'):
    return jsonify(getHistory(daysback))

@app.route('/about')
def ep_about():
    return render_template(
        'about.html',
        pagetitle='About Opabinia',
        pagetype='About',
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
    history=getHistory(daysback=None)['data']
    # 2. daily detail
    dates=dbGetDateList(db)
    perDay={
        tDate: getCounters(tDate.strftime(dateFormat))['data']
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
