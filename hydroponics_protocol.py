# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 18:11:19 2018

@author: 1brod
"""

# read in configuration from file
    # lights, pumps, etc.
from AtlasI2C import AtlasI2C
import sys
import datetime
import RPi.GPIO as GPIO
import os
from pathlib import Path

class duration():
    """A period of time defined by a beginning and ending time either on the same or subsequent day."""
    def __init__(self, start, end, duration):
        today=datetime.datetime.now()
        self.start=datetime.datetime(today.year, today.month, today.day, start)
        if start < end: # cycle is on the same day
            self.end=datetime.datetime(today.year, today.month, today.day, end)
        elif start > end: # cycle ends on the next day
            tomorrow=today+datetime.timedelta(1)
            self.end=datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, end)
        if (self.end - self.start).seconds/3600 != duration:
            msg='Duration must equal the duration between the end and start time. Duration = ' + str((self.end-self.start).seconds/3600)
            raise ValueError(msg)
        self.start=start
        self.end=end
        self.duration=duration

def time_in_duration(start, end):
    """Check if the current time is during the on duration."""
    today=datetime.datetime.now()
    if start < end: # cycle is on the same day
        end=datetime.datetime(today.year, today.month, today.day, end)
    elif start > end: # cycle ends on the next day
        tomorrow=today+datetime.timedelta(1)
        end=datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, end)
    start=datetime.datetime(today.year, today.month, today.day, start)    
    if today >= start and today < end:
        return True
    else:
        return False

class switch():
    """Any output device that has a pin number."""
    def __init__(self, pin):
        self.pin=pin
        self.flipped=False # default state is not flipped = off
        GPIO.setup(self.pin, GPIO.OUT) # check if line stays high or just activates once
    def activate(self):
        GPIO.output(self.pin, GPIO.HIGH) # check what this equals, if  = 1 or 0, for success or failure, then set self.flipped
        self.flipped=True
    def deactivate(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.flipped=False
        
class toggle():
    """Any input device that has a pin number."""
    def __init__(self, pin):
        self.pin=pin
        self.flipped=False # default state is not flipped = off
        GPIO.setup(self.pin, GPIO.IN) # check if line stays high or just activates once
    def read(self):
        return GPIO.input(self.pin)
        
class probe():
    """An Atlas Scientific Probe input device that communicates via I2C."""
    def __init__(self, sid, address, reps, coms, freq):
        try:
            assert isinstance(sid, str)
        except AssertionError:
            msg='Sensor ID must be a string.'
            raise TypeError(msg)
        self.pid=pid # probe id
        
        try:
            assert isinstance(address, int)
        except AssertionError:
            msg='Address must be an integer.'
            raise TypeError(msg)
        self.address=address
        
        try:
            assert isinstance(reps, int)
        except AssertionError:
            msg='Repititions must be an integer.'
            raise TypeError(msg)
        self.reps=reps
        
        try:
            assert isinstance(coms, AtlasI2C)
        except AssertionError:
            msg='Communication bus must be an AtlasI2C instance.'
            raise TypeError(msg)
        self.coms=coms
        
        try:
            assert isinstance(freq, float) or isinstance(freq, int)
        except AssertionError:
            msg='Frequency must be a floating point number or integer.'
            raise TypeError(msg)
        self.freq=freq
            
    def poll(self):
        """Poll for information from the AtlasI2C communications bus."""
        assert isinstance(self.freq, float) or isinstance(self.freq, int)
        # check for polling time being too short, change it to the minimum timeout if too short
        if self.freq < self.bus.long_timeout:
            print("Polling time is shorter than timeout, setting polling time to %0.2f" % self.bus.long_timeout)
            self.freq = self.bus.long_timeout
        cmd='poll' + str(self.freq)
        self.coms.set_i2c_address(self.address)
        reads=[] # can be averaged before storing data point
        for r in range(reps):
            reads[r]=(self.coms.query(cmd), datetime.datetime.now()) # list time received data too
        return reads
        
def print_to_file(path_to_file, probe, data, read_id):
    """Print information from the sensor to file."""
    # Sensor 3 |\t| Reading ID Num |\t| Data,data,data\n
    # Sensor 1 |\t| Reading ID Num |\t| Data,data,data\n
    delim=['\t', ',']
    with open(path_to_file, 'a') as fid:
        fid.write(probe.pid + delim[0] + str(read_id) + delim[0] + ''.join(data, delim[1]) + '\n')
    return 1

# data can be stored in a dictionary by address or id
# store the call # for syncing individual data points for each sensor

class lights(switch):
    def __init__(self, start, end, dur, pin):
        super().__init__(pin)
        self.duration=duration(start, end, dur)
    def check_status(): # perhaps should check GPIO.input(self.pin) too
        """Check status of lights."""
        should_be_flipped=time_in_duration(self.duration.start, self.duration.end)
        if should_be_flipped and not self.flipped:
            print('Something is wrong... Lights should be on, but pin is not showing being flipped.')
            return False
        elif not should_be_flipped and self.flipped:
            print('Something is wrong... Lights should not be on, but pin is showing being flipped.')
            return True
        elif should_be_flipped and self.flipped:
            return True
        elif not should_be_flipped and not self.flipped:
            return False

class pump(switch):
    def __init__():
        pass

class nutrient_pump(pump):
    def __init__():
        super.__init__()

class bilge_pump(pump):
    def __init__():
        super.__init__()

class stir_pump(pump):
    def __init__():
        super.__init__()

class water_level(toggle):
    def __init__():
        super.__init__()

def export_info():
    # inputs
    # outputs
    pass

def main():
    # initialization of the GPIO pins
    GPIO.setmode(GPIO.BOARD)
    home = str(Path.home())
    output_path= os.path.join(home, 'Google Drive', 'Project SIA', 'Code',  'probe_output.txt')
    
    atlas=AtlasI2C() # create communications bus
    
    # register probes
    poll_time=2
    freq=10
    
    do=probe('do', 97, 1, atlas, poll_time)
    orp=probe('orp', 98, 1, atlas, poll_time)
    ph=probe('ph', 99, 1, atlas, poll_time)
    ec=probe('ec', 100, 1, atlas, poll_time)
    rtd=probe('rtd', 102, 1, atlas, poll_time)
    co2=probe('co2', 105, 1, atlas, poll_time)
    
    # pH, ec, do, orp, co2 (co2 needs to wait 10 minutes upon startup)
    
    
    while True:
        pass
        

if __name__ == "__main__":
    # execute only if run as a script
    main()