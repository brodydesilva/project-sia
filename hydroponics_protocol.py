#!/usr/bin/env python3
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
import gpiozero
import os
import time
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
        if start < end: # cycle is on the same day
            self.hours = list(range(start, end))
        elif start > end: # cycle ends on the next day
            self.hours = list(range(start, 24)) + list(range(0,end))

def time_in_duration(hours):
    """Check if the current time is during the on duration."""
    today=datetime.datetime.now()
    if today.hour in hours:
        return True
    else:
        return False

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
    def __init__(self, pid, address, reps, coms, freq, out):
        try:
            assert isinstance(pid, str)
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
        self.reads=[]
        self.out=out
            
    def poll(self):
        """Poll for information from the AtlasI2C communications bus."""
        assert isinstance(self.freq, float) or isinstance(self.freq, int)
        # check for polling time being too short, change it to the minimum timeout if too short
        if self.freq < self.coms.long_timeout:
            print("Polling time is shorter than timeout, setting polling time to %0.2f" % self.coms.long_timeout)
            self.freq = self.coms.long_timeout
        cmd='poll' + str(self.freq)
        self.coms.set_i2c_address(self.address)
        self.reads.append((str(self.coms.query("R")), str(datetime.datetime.now()))) # list time received data too
        time.sleep(self.freq - self.coms.long_timeout)
        read=self.reads[-1] # store in case hits buffer length
        if len(self.reads) == self.reps: # write to file
            for x in range(0, self.reps):
                print_to_file(self.out, self.pid, self.reads[x])
            self.reads = [] # reset the buffer
        return read
        
def print_to_file(path_to_file, pid, data):
    """Print information from the sensor to file."""
    # Sensor 3\tData\ttimestamp\n
    # Sensor 1\tData\ttimestamp\n
    delim=['\t', ',']
    with open(path_to_file, 'a') as fid:
        fid.write(pid + delim[0] + delim[0].join(data) + '\n')
    return

# data can be stored in a dictionary by address or id
# store the call # for syncing individual data points for each sensor

class lights(gpiozero.DigitalOutputDevice):
    def __init__(self, start, end, dur, pin):
        super().__init__(pin)
        self.duration=duration(start, end, dur)
    def check_status(self): # perhaps should check GPIO.input(self.pin) too
        """Check status of lights. Return True if should flip, else False."""
        should_be_flipped=time_in_duration(self.duration.hours)
        if should_be_flipped and not self.value:
            # Lights should be on, but pin is not showing being flipped.
            return True
        elif not should_be_flipped and self.value:
            # Lights should not be on, but pin is showing being flipped.
            return True
        elif should_be_flipped and self.value:
            return False
        elif not should_be_flipped and not self.value:
            return False
    def flip_light(self):
        if self.value:
            self.off()
        elif not self.value:
            self.on()

class pumps(gpiozero.DigitalOutputDevice):
    def __init__(self, dur, pin):
        super().__init__(pin)
        self.watered_this_hour=False
        self.hour=datetime.datetime.now().hour
    def check_status(self):
        today=datetime.datetime.now()
        if not self.value: # not turned on
            if today.hour == self.hour: # not new hour
                if self.watered_this_hour:
                    pass
                else:
                    return True
            else:
                self.hour=today.hour # update hour
                return True
        return False
    def open_the_floodgates(self):
        self.on()
        time.sleep(20)
        self.off()
        self.watered_this_hour=True

def main():
    home = str(Path.home())
    output_path = os.path.join(home, 'Documents',  'probe_output.txt')
    
    atlas=AtlasI2C() # create communications bus
    
    # register probes
    poll_time=2
    freq=1
    
    reservoir_pump=pumps(20, 5) # digital pin 5

    lights_long=lights(18, 14, 20, 17)
    lights_med=lights(18, 12, 18, 27)
    lights_short=lights(18, 10, 16, 22)
    lighting=[lights_long, lights_med, lights_short]

    do=probe('do', 97, freq, atlas, poll_time, output_path)
    orp=probe('orp', 98, freq, atlas, poll_time, output_path)
    ph=probe('ph', 99, freq, atlas, poll_time, output_path)
    ec=probe('ec', 100, freq, atlas, poll_time, output_path)
    rtd=probe('rtd', 102, freq, atlas, poll_time, output_path)
    co2=probe('co2', 105, freq, atlas, poll_time, output_path)
    
    sensors=[do, orp, ph, rtd, ec, co2]
    while True:
        try:
            while True:
                for s in sensors:
                    s.poll()
                for light in lighting:
                    if light.check_status(): # if True, flip switch
                        light.flip_light()
                if reservoir_pump.check_status():
                    reservoir_pump.open_the_floodgates()
                print('Successfully polled sensors.\nHibernating.')
        except Exception as e:
            print('Something went wrong!')
            print(datetime.datetime.now())

if __name__ == "__main__":
    # execute only if run as a script
    main()
