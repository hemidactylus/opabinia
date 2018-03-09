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

if __name__=='__main__':
   testTrigger=12
   testEcho=25
   pi=pigpio.pi()
   distancer = DistanceSensor(pi,testTrigger,testEcho)
   while(True):
      print("d=%.5f" % distancer.measure())
      time.sleep(0.2)
