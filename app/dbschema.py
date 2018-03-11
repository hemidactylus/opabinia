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
    'history': {
        'primary_key': [
            ('date', 'DATE'),
        ],
        'columns': [
            ('count','INTEGER'),
            ('abscount','INTEGER'),
            ('max','INTEGER'),
            ('ins','INTEGER'),
        ],
        'indices': {
            'history_date_index': [
                ('date', 'ASC'),
            ],
        },
    },
}
