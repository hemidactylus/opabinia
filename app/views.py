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
)

@app.route('/')
@app.route('/counters')
@app.route('/counters/<date>')
def ep_counters(date='default'):
    db=dbOpenDatabase(dbName)
    reqDate,lastMidnight=timeBounds(date)
    entries=sorted(
        [
            localiseRow(row)
            for row in integrateRows(
                db,
                reqDate,
            )
        ],
        key=lambda evt: evt['time'],
        reverse=True,
    )
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetitle='Counts for %s' % (reqDate.strftime(niceDateFormat)),
      baseurl=url_for('ep_counters'),
      twocolumns=False, # three-col layout
      reqdate=reqDate.strftime(dateFormat),
      entries=entries,
    )

@app.route('/events')
@app.route('/events/<date>')
def ep_events(date='default'):
    db=dbOpenDatabase(dbName)
    reqDate,lastMidnight=timeBounds(date)
    entries=sorted(
        [
            locRow
            for locRow in (
                localiseRow(row)
                for row in dbGetRows(
                    db,
                    reqDate
                )
            )
        ],
        key=lambda evt: evt['time'],
        reverse=True,
    )
    #
    return render_template(
      "graphlist.html",
      text='Entries: %i' % (len(entries)),
      pagetitle='Hits for %s' % (reqDate.strftime(niceDateFormat)),
      baseurl=url_for('ep_events'),
      twocolumns=True, # this means: pointlike events, two-column layout
      reqDate=reqDate.strftime(dateFormat),
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
