'''
    spreadsheets.py : utils to generate spreadsheets as bytesIO
'''

from io import BytesIO
import xlsxwriter
from datetime import datetime

from config import niceDateFormat
from dateutils import localiseDate,findPreviousMidnight

def bringToToday(dt):
    hms=dt.timetuple()[3:6]
    thisDay=datetime.now().timetuple()[:3]
    return datetime(*(thisDay+hms))

def makeSpreadsheet(history, perDay, now):
    '''
        preparation of the whole spreadsheet
    '''
    output = BytesIO()
    workbook = xlsxwriter.Workbook(
      output,
      {
          'strings_to_numbers': True,
          'strings_to_urls': True,
          'default_date_format': 'mmm d, yyyy hh:mm:ss',
          'remove_timezone': True,
      }
    )
    # formats
    wTitleFormat=workbook.add_format({'bold':True,'font_size':18})
    wNoteFormat=workbook.add_format({'font_size':8})
    wHeadingFormat=workbook.add_format({'italic':True})
    wDateFormat=workbook.add_format({'num_format': 'd-m-yyyy', 'font_color': 'blue', 'bold': True})
    wTimeFormat=workbook.add_format({'num_format': 'hh:mm:ss', 'font_color': 'blue', 'bold': True})
    wDateTimeNoteFormat=workbook.add_format({'font_size':8, 'num_format': 'mmm d, yyyy hh:mm:ss'})
    wDateNoteFormat=workbook.add_format({'font_size':8, 'num_format': 'mmm d, yyyy'})
    # history.
    numHistoryItems=len(history)
    hWorksheet = workbook.add_worksheet('History')
    hWorksheet.insert_image(0,0,'app/static/images/opabinia_small.png')
    hWorksheet.write(0,0,'Opabinia',wTitleFormat)
    hWorksheet.set_row(0,36)
    hWorksheet.write(1,0,'Full history as of:',wNoteFormat)
    hWorksheet.write(1,1,now,wDateTimeNoteFormat)
    hWorksheet.set_column(0, 0, 16)
    hWorksheet.write(2,0,'Day',wHeadingFormat)
    hWorksheet.set_column(0, 1, 16)
    hWorksheet.write(2,1,'Max in',wHeadingFormat)
    hWorksheet.write(2,2,'In hits',wHeadingFormat)
    hWorksheet.write(2,3,'Hits',wHeadingFormat)
    hWorksheet.write(2,4,'Bias',wHeadingFormat)
    for row,(hDay,hElem) in enumerate(sorted(
        history.items(),
        reverse=True,
    )):
        hWorksheet.write(3+row,0,hDay,wDateFormat)
        hWorksheet.write(3+row,1,hElem['max'])
        hWorksheet.write(3+row,2,hElem['ins'])
        hWorksheet.write(3+row,3,hElem['abscount'])
        hWorksheet.write(3+row,4,hElem['count'])
    # History chart
    historyChartsheet=workbook.add_chartsheet('History chart')
    historyChart = workbook.add_chart({'type': 'column'})
    for hPlotObs,hColIndex,hColColor in zip(
        ['Max in','In hits','Hits','Bias'],
        [1,2,3,4],
        ['#202020','#505050','#808080','#B0B0B0'],
    ):
        historyChart.add_series({
            'name': hPlotObs,
            'categories': ['History',3,0,2+numHistoryItems,0],
            'values': ['History',3,hColIndex,2+numHistoryItems,hColIndex],
            'fill':       {'color': hColColor},
        })
    historyChart.set_x_axis({
        'name': 'Date',
        'name_font': {'bold': True},
        'num_font':  {'italic': True },
        'reverse': False,
    })
    historyChart.set_title ({'name': 'History chart'})
    historyChartsheet.set_chart(historyChart)
    # daily curves, chartsheet for later
    dailyChartsheets={}
    dailyCharts={}
    for dailyChartName, dailyChartColIndex in zip(
        ['Total hits','In hits','People in'],
        [2,3,4],
    ):
        dailyChartsheets[dailyChartName]=workbook.add_chartsheet('%s, trend chart' % dailyChartName)
        dailyCharts[dailyChartName]=workbook.add_chart(
            {'type':'scatter','subtype': 'straight_with_markers'}
        )
        dailyCharts[dailyChartName].set_legend({'none': True})
    # daily, one per worksheet
    for tDate,tEvents in sorted(perDay.items(),reverse=True):
        workSheetName=tDate.strftime(niceDateFormat)
        tWorksheet=workbook.add_worksheet(workSheetName)
        tWorksheet.set_row(0,26)
        tWorksheet.write(0,0,'Opabinia',wTitleFormat)
        tWorksheet.write(1,0,'Daily activity for:',wNoteFormat)
        tWorksheet.set_column(0, 0, 16)
        tWorksheet.write(1,1,tDate,wDateNoteFormat)
        tWorksheet.set_column(0, 1, 16)
        tWorksheet.write(2,0,'Time',wHeadingFormat)
        tWorksheet.write(2,1,'Hour',wHeadingFormat)
        tWorksheet.write(2,2,'Total hits',wHeadingFormat)
        tWorksheet.write(2,3,'In hits',wHeadingFormat)
        tWorksheet.write(2,4,'People in',wHeadingFormat)
        numEvents=len(tEvents)
        for row,evt in enumerate(tEvents):
            tWorksheet.write(3+row,0,evt['time'],wTimeFormat)
            tWorksheet.write(3+row,1,bringToToday(evt['time']),wTimeFormat)
            tWorksheet.write(3+row,2,evt['abscount'])
            tWorksheet.write(3+row,3,evt['ins'])
            tWorksheet.write(3+row,4,evt['count'])
        # add to daily charts
        for dailyChartName, dailyChartColIndex in zip(
            ['Total hits','In hits','People in'],
            [2,3,4],
        ):
            dailyCharts[dailyChartName].add_series({
                # we skip the last row since it is the 'midnight' zero of integration
                'name': workSheetName,
                'categories': [workSheetName,3,1,1+numEvents,1],
                'values': [workSheetName,3,dailyChartColIndex,1+numEvents,dailyChartColIndex],
            })
    # we attach the daily chart to the chartsheet
    for dailyChartName, dailyChartColIndex in zip(
        ['Total hits','In hits','People in'],
        [2,3,4],
    ):
        dailyCharts[dailyChartName].set_x_axis({
            'date_axis': True,
            'num_format': 'hh:mm:ss',
        })
        dailyCharts[dailyChartName].set_title({'name': '%s, trend chart' % dailyChartName})
        dailyChartsheets[dailyChartName].set_chart(dailyCharts[dailyChartName])
    # done.
    workbook.close()
    output.seek(0)
    return output
