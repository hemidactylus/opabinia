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

# sensor setup
#    (Right=0 and Left=1 sensor pin setup.
#     L/R refer to someone looking at the sensors).
sensorPins=[
    {
        'trigger': 18,
        'echo':    24,
    },
    {
        'trigger': 12,
        'echo':    25,
    },
]
# which way is 'entering' (i.e. +1)?
innerSensor=0 # i.e. the R one is the one closer to 'in'
# sensor response setup
sensorReadFrequency=0.002           # seconds
sensorDistanceRange=[0.10,1.20]     # meters: min/max
sensorDebounceTime=0.05             # seconds
sensorRefractoryTime=2.0            # seconds
sensorPassageWindow=[0.1,0.8]       # seconds
# expwindow sensor settings
sensorDampRate=0.6
sensorThresholdFactor=0.3
# status-signaling LEDs
ledPins={
    'baseline': [21],       # baseline, operation (green) - only one
    # these are [R, L] in the same way as the sensorPins above
    'signal':   [20, 26],   # instantaneous measurement (yellow)
    'detect':   [16, 19],   # debounced status (red)
}
