#!/usr/bin/env python3
# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
from PCA9685 import PCA9685

### Use BCM GPIO references
### instead of physical pin number
GPIO.setmode(GPIO.BOARD)
##
### Define GPIO signals to use
### Physical pins 11,15,16,18
### GPIO17,GPIO22,GPIO23,GPIO24
##StepPins = [11, 15, 16, 18]
##
### Set all pins as output
##for pin in StepPins:
##  print "Setup pins"
##  GPIO.setup(pin,GPIO.OUT)
##  GPIO.output(pin, False)
##
### Define advanced sequence
### as shown in manufacturers datasheet
Seq = [[True,False],
       [True,True],
       [False,True],
       [False,False]]
##
##StepCount = len(Seq)
##StepDir = -1 # Set to 1 or 2 for clockwise
##            # Set to -1 or -2 for anti-clockwise
##
### Read wait time from command line
##if len(sys.argv)>1:
##  WaitTime = int(sys.argv[1])/float(1000)
##else:
##  WaitTime = 10/float(1000)
##
### Initialise variables
##StepCounter = 0
##StepDir = 1
### Start main loop
##for i in range(512):
##  print StepCounter,
##  print Seq[StepCounter]
##  if i >= 256:
##      StepDir = -1
##
##
##  for pin in range(0, 2):
##    xpin = StepPins[pin]
##    if Seq[StepCounter][pin-1]!=0:
##      print " Enable GPIO %i" %(xpin)
##      GPIO.output(xpin, True)
##    else:
##      GPIO.output(xpin, False)
##  print " StepDir %i, StepCounter %i" %(StepDir, StepCounter)
##  StepCounter += StepDir
##  # If we reach the end of the sequence
##  # start again
##  if (StepCounter>=StepCount):
##    StepCounter = 0
##  if (StepCounter<0):
##    StepCounter = StepCount+StepDir
##
##  # Wait before moving on
##  time.sleep(WaitTime)
class PanTilt:
    def __init__(self,interstep_delay=0.2,ranges=[180,180]):
        self.interstep_delay = interstep_delay
        self.ranges = ranges
        #Instantiate the lower-level HAT controller device and set the angle to 0,0
        dev = PCA9685()
        dev.setPWMFreq(50)
        dev.setRotationAngle(0, 0)
        dev.setRotationAngle(1, 0)
        self.dev = dev
        self.angles = [0,0] #Indicate current 
        return

    def __del__(self):
        dev.setRotationAngle(0, 0)
        dev.setRotationAngle(1, 0)
        del(self.dev)
        return

    def rotate(self, axis, steps):
        future_angle = max(0,self.angles[axis] + steps)
        future_angle = min(future_angle, self.ranges[axis])
        if steps >= 0:
            range_iter = range(self.angles[axis] + 1, future_angle + 1, 1)
        else:
            range_iter = range(self.angles[axis] - 1, future_angle - 1, -1)
        for a in range_iter:
            self.dev.setRotationAngle(axis,a)
            time.sleep(self.interstep_delay)
        self.angles[axis] = future_angle
        return

  
def pan(pantilthat, degrees):
    pantilthat.setRotationAngle(0, degrees)
    return
    
def tilt(pantilthat, degrees):
    pantilthat.setRotationAngle(1, degrees)
    return

def zoom_focus(steps, pins):
    WaitTime = 10/float(1000)
    if steps < 0:
        start = abs(steps)-1
        stop = -1
        StepDir = -1
    else:
        start = 0
        stop = steps
        StepDir = 1

    for step in range(start,stop,StepDir):
      for i in range(0,len(pins)):
          pin = pins[i]
          next_step = step % len(Seq)
          GPIO.output(pin, Seq[step % len(Seq)][i])
      # Wait before moving on
      time.sleep(WaitTime)
    return

def zoom(steps):
    zoom_focus(steps, [11,13])
    return

def focus(steps):
    zoom_focus(steps, [15,40])
    return

def init():
    StepPins = [11, 13, 15, 40]
    for pin in StepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, False)
    pwm = PCA9685()
    pwm.setPWMFreq(50)
    pwm.setRotationAngle(0, 0)
    pwm.setRotationAngle(1, 0)
    return(pwm)

def clean_up():
    GPIO.cleanup()
    
def main(argv):
    degrees_tilt = 0
    degrees_pan = 0
    pwm = init()
    
    while True:
        user_input = input("Control camera command:")
        if user_input == 's':
            degrees_tilt = degrees_tilt + 1
            tilt(pwm, degrees_tilt)
        elif user_input == 'w':
            degrees_tilt = degrees_tilt - 1
            tilt(pwm, degrees_tilt)
        elif user_input == 'd':
            degrees_pan = degrees_pan + 1
            pan(pwm, degrees_pan)
        elif user_input == 'a':
            degrees_pan = degrees_pan - 1
            pan(pwm, degrees_pan)
        elif user_input == 'o':       
            zoom(256)
        elif user_input == 'i':
            zoom(-256)
        elif user_input == 'k':
            focus(256)
        elif user_input == 'l':
            focus(-256)
        elif user_input == 'q':
            break

    clean_up()

if __name__ == "__main__":
    main(sys.argv)
