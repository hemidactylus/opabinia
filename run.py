#!/usr/bin/env python

import sys

# failsafe db creation
from app.config import dbName
from app.dboperations import checkAndOpenDatabase
checkAndOpenDatabase(dbName)

from app import app

if __name__=='__main__':
    # if -e flag is specified, enable running as
    # externally-accessible (still non-production) host
    host=None
    if '-e' in sys.argv[1:]:
        host='0.0.0.0'
    app.run(debug=True,host=host)
