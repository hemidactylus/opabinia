#!/usr/bin/python

'''
    measurer.py : the independent stand-alone forever-running
    script that measures and updates the DB

    In order to use the GPIO pins, this must run as root

'''

import time
import pigpio

from config import (
    dbName,
    #
    sensorPins,
    innerSensor,
    #
    sensorReadFrequency,
    sensorDistanceRanges,
    sensorDebounceTime,
    sensorRefractoryTime,
    sensorPassageWindow,
    #
    sensorDampRate,
    sensorThresholdFactor,
    #
    ledPins,
)
from dboperations import (
    checkAndOpenDatabase,
    dbOpenDatabase,
    dbSaveRow,
)
from DistanceSensor import (
    DistanceSensor,
    DebouncedSensor,
)

if __name__=='__main__':

    print('Init.')
    db=checkAndOpenDatabase(dbName)
    pi=pigpio.pi()

    distancers=[
        DistanceSensor(pi,sPins['trigger'],sPins['echo'])
        for sPins in sensorPins
    ]
    debounceds=[
        DebouncedSensor(
            sensorDistanceRange,
            sensorDebounceTime,
            distancer,
            sensorRefractoryTime,
            avgDampRate=sensorDampRate,
            avgThresholdFactor=sensorThresholdFactor,
        )
        for distancer,sensorDistanceRange in zip(
            distancers,
            sensorDistanceRanges,
        )
    ]

    # led setup
    for ledPin in (ledPin for ledPinGroup in ledPins.values() for ledPin in ledPinGroup):
        pi.set_mode(ledPin,pigpio.OUTPUT)
        pi.write(ledPin,0)

    # callbacks to register in the debounceds
    def debouncedCallback(debIndex,debounceds=debounceds,pi=pi,ledPins=ledPins,db=db):
        '''
            debIndex is the index in 'debounced' of who triggered the callback
        '''
        thisDeb=debounceds[debIndex]
        # if this sensor went UP and the other one went UP in a recency timewindow,
        # call it a +/- 1 and commit it.
        if thisDeb.debStatus:
            activationDelay=thisDeb.lastDebouncedHigh - debounceds[1-debIndex].lastDebouncedHigh
            if activationDelay <= sensorPassageWindow[1] and activationDelay >= sensorPassageWindow[0]:
                # +/-1 event detected. Direction is determined
                # based on which sensor was this, and what is the 'inside'-facing sensor.
                direction=(2*debIndex-1)*(2*innerSensor-1)
                dbSaveRow(db,{'count':direction,'abscount':1})
                db.commit()
        #
        handleBaselineLed()
        pi.write(ledPins['detect'][debIndex],thisDeb.debStatus)

    def changeCallback(debIndex,debounceds=debounceds,pi=pi,ledPins=ledPins,db=db):
        thisDeb=debounceds[debIndex]
        handleBaselineLed()
        pi.write(ledPins['signal'][debIndex],thisDeb.instaStatus)

    def handleBaselineLed(debounceds=debounceds,ledPins=ledPins):
        tTime=time.time()
        noActivity=not any(deb.instaStatus or deb.debStatus for deb in debounceds)
        pi.write(ledPins['baseline'][0],noActivity * (int(tTime*2) % 2) )

    for dIndex,deb in enumerate(debounceds):
        deb.onDebouncedChange(lambda d=dIndex: debouncedCallback(d))
        deb.onChange(lambda d=dIndex: changeCallback(d))

    while True:
        for deb in debounceds:
            deb.update()
            handleBaselineLed()
            time.sleep(sensorReadFrequency)
