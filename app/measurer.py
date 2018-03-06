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
    sensorTrigger,
    sensorEcho,
    #
    sensorReadFrequency,
    sensorDistanceRange,
    sensorDebounceTime,
    sensorRefractoryTime,
    #
    sensorDampRate,
    sensorThresholdFactor,
    #
    statusLed,
    debStatusLed,
    baseStatusLed,
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
            self.callback(self.instaStatus,self.debStatus)
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
                        self.debCallback(self.instaStatus,self.debStatus)

if __name__=='__main__':

    print('Init.')
    pi=pigpio.pi()
    distancer=DistanceSensor(pi,sensorTrigger,sensorEcho)

    db=checkAndOpenDatabase(dbName)

    # led setup
    pi.set_mode(statusLed,pigpio.OUTPUT)
    pi.set_mode(debStatusLed,pigpio.OUTPUT)
    pi.write(statusLed,0)
    pi.write(debStatusLed,0)

    deb = DebouncedSensor(
        sensorDistanceRange,
        sensorDebounceTime,
        distancer,
        sensorRefractoryTime,
        avgDampRate=sensorDampRate,
        avgThresholdFactor=sensorThresholdFactor,
        )

    def increaseCallbacker(instaStatus,debStatus,pi=pi,statusLed=debStatusLed,baseLed=baseStatusLed):
        if debStatus:
            # register a +1 increment in passage counts
            dbSaveRow(db,{'count':1,'abscount':1})
            print('Saving now a +1')
            db.commit()
        pi.write(baseLed,not(instaStatus or debStatus))
        pi.write(statusLed,int(debStatus))

    def statusCallbacker(instaStatus,debStatus,pi=pi,statusLed=statusLed,baseLed=baseStatusLed):
        pi.write(baseLed,not(instaStatus or debStatus))
        pi.write(statusLed,int(instaStatus))

    deb.onDebouncedChange(increaseCallbacker)
    deb.onChange(statusCallbacker)

    while True:
        deb.update()
        time.sleep(sensorReadFrequency)
