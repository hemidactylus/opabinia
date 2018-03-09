'''
  config.py - publicly available things
'''

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

dbName = os.path.join(basedir,'database','opabinia.db')

timeZone='Europe/Rome'

dateFormat='%Y-%m-%d'
niceDateFormat='%B %d, %Y'

# UI settings
defaultHoursBack=8
recentnessTimeSpan=timedelta(hours=defaultHoursBack)
maxRecentItems=None # None=no cuts applied

# sensor setup (this'll become an array of two)
sensorTriggerR=   18
sensorEchoR=      24
sensorTriggerL=   12
sensorEchoL=      25
# sensor response setup
sensorReadFrequency=0.005           # seconds
sensorDistanceRange=[0.10,0.95]     # meters: min/max
sensorDebounceTime=0.05             # seconds
sensorRefractoryTime=2.0            # seconds
# expwindow sensor settings
sensorDampRate=0.6
sensorThresholdFactor=0.3
# status-signaling LEDs
statusLed=20      # instantaneous measurement (yellow)
debStatusLed=16   # debounced status (red)
baseStatusLed=21  # baseline, operation (green)
