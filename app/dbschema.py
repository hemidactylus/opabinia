'''
  dbschema.py
'''

dbTablesDesc={
    'counts': {
        'primary_key': [
            ('time', 'TIMESTAMP'),
        ],
        'columns': [
            ('count','INTEGER'),
            ('abscount','INTEGER'),
        ],
        'indices': {
            'time_index': [
                ('time', 'ASC'),
            ],
        },
    },
}
