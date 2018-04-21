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
fileNameDateFormat='%Y_%m_%d_%H_%M_%S'

# web app settings
barSeconds=30*60 # for the histogram on 'Flux' page
maxNumCounterEntries=500   # above this many counter
                            # entries in one day, the
                            # shortest-lived are pruned away cleanly

# sensor setup
#    (Left=0 and Right=1 sensor pin setup.
#     L/R refer to someone looking at the sensors).
sensorPins=[
    {
        'trigger': 12,
        'echo':    25,
    },
    {
        'trigger': 18,
        'echo':    24,
    },
]
# which way is 'entering' (i.e. +1)?
innerSensor=0 # i.e. the L one is the one closer to 'in'
# sensor response setup
sensorReadFrequency=0.002           # seconds
sensorDistanceRanges=[              # meters: min/max, per sensor
    [0.25,0.95],
    [0.25,0.95],
]
sensorDebounceTime=0.02             # seconds
sensorRefractoryTime=0.1            # seconds
sensorPassageWindow=[0.025,0.6]     # seconds
# expwindow sensor settings
sensorDampRate=0.8
sensorThresholdFactor=0.2
# status-signaling LEDs
ledPins={
    'baseline': [21],       # baseline, operation (green) - only one
    # these are [R, L] in the same way as the sensorPins above
    'signal':   [19, 20],   # instantaneous measurement (yellow)
    'detect':   [26, 16],   # debounced status (red)
}
