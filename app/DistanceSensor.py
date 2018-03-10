'''
   DistanceSensor.py : a class with the interface for initialising
   and reading off a distance sensor of type HC-SR04 in two-pin mode.
'''

import time
import pigpio

class DistanceSensor:
   def __init__(self,pi,trigger,echo):
      self.trigger=trigger
      self.echo=echo
      self.pi=pi
      #
      self._high=self.pi.get_current_tick() 
      self._time=self.pi.get_current_tick() 
      self._done=self.pi.get_current_tick() 
      #
      self.pi.callback(self.echo,pigpio.RISING_EDGE,self.onRising)
      self.pi.callback(self.echo,pigpio.FALLING_EDGE,self.onFalling)
      #
   def onRising(self,gpio,level,tick):
      # this is to be attached as a callback
      self._high=tick
   def onFalling(self,gpio,level,tick):
      # this is to be attached as a callback
      self._time=tick-self._high
      self._done=True
   def measure(self):
      self._done=False
      self.pi.set_mode(self.trigger, pigpio.OUTPUT)
      self.pi.gpio_trigger(self.trigger,50,1)
      self.pi.set_mode(self.echo, pigpio.INPUT)
      time.sleep(0.0001)
      tim = 0
      while not self._done:
         time.sleep(0.001)
         tim = tim+1
         if tim > 50:
            return 0
      self._done=None
      return self._time/5830.0 # metres

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
   testTrigger=12
   testEcho=25
   pi=pigpio.pi()
   distancer = DistanceSensor(pi,testTrigger,testEcho)
   while(True):
      print("d=%.5f" % distancer.measure())
      time.sleep(0.2)
