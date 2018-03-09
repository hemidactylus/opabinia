'''
    spreadsheets.py : utils to generate spreadsheets as bytesIO
'''

from io import BytesIO
import xlsxwriter

def testSpreadsheet():

    from datetime import datetime

    output = BytesIO()
    workbook = xlsxwriter.Workbook(
      output,
      {
          'strings_to_numbers': True,
          'strings_to_urls': True,
          'default_date_format': 'mmm d, yyyy hh:mm:ss',
      }
    )
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Hollo')
    worksheet.write('B1', '123')
    worksheet.write('C1', '+12')
    worksheet.write('D1', '-66')
    worksheet.write('E1', 'https://github.com/hemidactylus/opabinia')
    worksheet.write('F1', datetime(2018,3,9,11,33,44))
    workbook.close()
    output.seek(0)
    return output
