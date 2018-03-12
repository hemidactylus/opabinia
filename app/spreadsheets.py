'''
    spreadsheets.py : utils to generate spreadsheets as bytesIO
'''

from io import BytesIO
import xlsxwriter

from config import niceDateFormat

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
    # history.
    hworksheet = workbook.add_worksheet('History')
    hworksheet.write(0,0,'Opabinia')
    hworksheet.write(1,0,'Full history as of:')
    hworksheet.write(1,1,now)
    hworksheet.write(2,0,'Day')
    hworksheet.write(2,1,'Max in')
    hworksheet.write(2,2,'In hits')
    hworksheet.write(2,3,'Hits')
    hworksheet.write(2,4,'Bias')
    for row,(hDay,hElem) in enumerate(sorted(
        history.items(),
        reverse=True,
    )):
        hworksheet.write(3+row,0,hDay)
        hworksheet.write(3+row,1,hElem['max'])
        hworksheet.write(3+row,2,hElem['ins'])
        hworksheet.write(3+row,3,hElem['abscount'])
        hworksheet.write(3+row,4,hElem['count'])
    # daily, one per worksheet
    for tDate,tEvents in sorted(perDay.items(),reverse=True):
        tWorksheet=workbook.add_worksheet(tDate.strftime(niceDateFormat))
        tWorksheet.write(0,0,'Daily activity for:')
        tWorksheet.write(0,1,tDate)
        tWorksheet.write(1,0,'Time')
        tWorksheet.write(1,1,'Total hits')
        tWorksheet.write(1,2,'In hits')
        tWorksheet.write(1,3,'People in')
        for row,evt in enumerate(tEvents):
            tWorksheet.write(2+row,0,evt['time'])
            tWorksheet.write(2+row,1,evt['abscount'])
            tWorksheet.write(2+row,2,evt['ins'])
            tWorksheet.write(2+row,3,evt['count'])
    # done.
    workbook.close()
    output.seek(0)
    return output
