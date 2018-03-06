from app import app as application

from app.views import checkDB
from app.config import dbName

if __name__=='__main__':
    checkDB(dbName)
    application.run()
