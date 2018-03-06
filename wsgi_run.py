from app import app as application

from app.dboperations import (
    checkAndOpenDatabase,
)
from app.config import (
    dbName
)

if __name__=='__main__':
    checkAndOpenDatabase(dbName)
    application.run()
