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
    sensorDistanceRange,
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
from DistanceSensor import DistanceSensor

class DebouncedSensor:

    def __init__(
        self,
        activeInterval,
        debounceTime,
        distanceSensor,
        refractoryTime,
        avgDampRate=0.5,
        avgThresholdFactor=0.8):
        '''
            activeInterval = [min_in_meters, max_in_meters]
                within which the reading yields "active"
            debounceTime = seconds
                time after which an uninterrupted status is
                taken as 'serious' and moved up to the debounced reading
            distanceSensor = d
                a DistanceSensor instance, initialised and ready
                (or anything that responds in meters to a measure() call)
            refractoryTime = seconds
                minimum time that must pass between two events debStatus->True
            avgDampRate
            avgThresholdFactor
                these provide the settings for the moving-exp-average
                check to absorb intermittent reading.
                At each reading an exp-moving-window
                with the desired damp factor is made upon
                the pointlike measurement (instaStatus)
                and the newStatus is read off whether
                such average goes above a certain
                fraction of its max value 1/(1-dampRate)
        '''
        self.min,self.max=activeInterval
        self.sensor=distanceSensor
        self.status=None
        self.debStatus=None
        self.debTime=debounceTime
        self.refTime=refractoryTime
        now=time.time()
        self.lastChange=now
        self.lastDebChange=now
        self.lastDebouncedHigh=now
        #
        self.instaStatus=None
        self.avgStatus=0.0
        self.avgRate=avgDampRate
        self.avgThreshold=avgThresholdFactor/(1-self.avgRate)
        #
        self.callback=None
        self.debCallback=None

    def onDebouncedChange(self,callback):
        '''
            registers a callback on any debStatus actual change.
            The callback must accept two arguments:
                instantaneous status, debounced status
        '''
        self.debCallback=callback

    def onChange(self,callback):
        '''
            same as above for the pre-debounce signal changes
        '''
        self.callback=callback

    def update(self):
        tMeasure=self.sensor.measure()
        instaStatus=tMeasure>=self.min and tMeasure<=self.max
        if instaStatus!=self.instaStatus:
            self.instaStatus=instaStatus
            self.callback()
        #
        self.avgStatus=self.avgRate*self.avgStatus+self.instaStatus
        newStatus=self.avgStatus>self.avgThreshold
        #
        now=time.time()
        if newStatus != self.status:
            # mark this pre-debounce change
            self.lastChange=now
            self.status=newStatus
            # if self.callback is not None:
            #     self.callback(self.status)
        if now-self.lastChange>=self.debTime:
            if self.debStatus != self.status:
                # if either we are going down or enough time has passed since last ->up
                if not self.status or (now-self.lastDebouncedHigh)>=self.refTime:
                    # Here a change in debounced status is detected
                    self.debStatus=self.status
                    if self.debStatus:
                        self.lastDebouncedHigh=now
                    if self.debCallback is not None:
                        self.debCallback()

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
        for distancer in distancers
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
