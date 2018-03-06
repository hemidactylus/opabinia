'''
  dbschema.py
'''

dbTablesDesc={
    'counts': {
        'primary_key': [
            ('time', 'TIMESTAMP'),
        ],
        'columns': [
            ('date', 'DATE'),
            ('count','INTEGER'),
            ('abscount','INTEGER'),
        ],
        'indices': {
            'time_index': [
                ('time', 'ASC'),
            ],
            'date_index': [
                ('date', 'ASC'),
            ],
        },
    },
}
