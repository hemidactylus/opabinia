import os
from flask import Flask
from flask_bootstrap import Bootstrap

from app.config import dbName

app = Flask(__name__,static_folder='static', static_url_path='/static')
Bootstrap(app)

# this must be AFTER the above, otherwise 'db' is circularly not found in the imports
from app import views
