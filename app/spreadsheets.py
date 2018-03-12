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
    # formats
    wTitleFormat=workbook.add_format({'bold':True,'font_size':18})
    wNoteFormat=workbook.add_format({'font_size':8})
    wHeadingFormat=workbook.add_format({'italic':True})
    wDateFormat=workbook.add_format({'num_format': 'd-m-yyyy', 'font_color': 'blue', 'bold': True})
    wTimeFormat=workbook.add_format({'num_format': 'hh:mm:ss', 'font_color': 'blue', 'bold': True})
    wDateTimeNoteFormat=workbook.add_format({'font_size':8, 'num_format': 'mmm d, yyyy hh:mm:ss'})
    wDateNoteFormat=workbook.add_format({'font_size':8, 'num_format': 'mmm d, yyyy'})
    # history.
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
    # daily, one per worksheet
    for tDate,tEvents in sorted(perDay.items(),reverse=True):
        tWorksheet=workbook.add_worksheet(tDate.strftime(niceDateFormat))
        tWorksheet.set_row(0,26)
        tWorksheet.write(0,0,'Opabinia',wTitleFormat)
        tWorksheet.write(1,0,'Daily activity for:',wNoteFormat)
        tWorksheet.set_column(0, 0, 16)
        tWorksheet.write(1,1,tDate,wDateNoteFormat)
        tWorksheet.set_column(0, 1, 16)
        tWorksheet.write(2,0,'Time',wHeadingFormat)
        tWorksheet.write(2,1,'Total hits',wHeadingFormat)
        tWorksheet.write(2,2,'In hits',wHeadingFormat)
        tWorksheet.write(2,3,'People in',wHeadingFormat)
        for row,evt in enumerate(tEvents):
            tWorksheet.write(3+row,0,evt['time'],wTimeFormat)
            tWorksheet.write(3+row,1,evt['abscount'])
            tWorksheet.write(3+row,2,evt['ins'])
            tWorksheet.write(3+row,3,evt['count'])
    # done.
    workbook.close()
    output.seek(0)
    return output
