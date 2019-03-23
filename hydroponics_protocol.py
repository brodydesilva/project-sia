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
import boto3
import csv
from pathlib import Path
from picamera import PiCamera

class Duration():
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
        
class Probe():
    """An Atlas Scientific Probe input device that communicates via I2C."""
    def __init__(self, pid, address, coms, freq, aws_end):
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
        
        try:
            assert isinstance(aws_end, str)
            if aws_end != 'dynamodb' and aws_end != 's3':
                msg='AWS Endpoint must either be \'dynamodb\' or \'s3\'.'
                raise TypeError(msg)
        except AssertionError:
            msg='AWS Endpoint must be a string.'
            raise TypeError(msg)
        
        self.freq=freq
        self.reads=[]
            
    def poll(self):
        """Poll for information from the AtlasI2C communications bus."""
        assert isinstance(self.freq, float) or isinstance(self.freq, int)
        # check for polling time being too short, change it to the minimum timeout if too short
        if self.freq < self.coms.long_timeout:
            print("Polling time is shorter than timeout, setting polling time to %0.2f" % self.coms.long_timeout)
            self.freq = self.coms.long_timeout
        self.coms.set_i2c_address(self.address)
        read=(self.pid, str(self.coms.query("R")), str(datetime.datetime.now()), self.aws_end) # sensor_id, value, timestamp, aws_endpoint
        time.sleep(self.freq - self.coms.long_timeout)
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

class Lights(gpiozero.DigitalOutputDevice):
    def __init__(self, start, end, dur, pin):
        super().__init__(pin)
        self.duration=Duration(start, end, dur)
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
            # insert web ping here
        elif not self.value:
            self.on()
            # insert web ping here

class Pumps(gpiozero.DigitalOutputDevice):
    def __init__(self, dur, pin):
        super().__init__(pin)
        self.duration=dur
        self.watered_this_hour=False
        self.watered_this_half=False
        self.hour=datetime.datetime.now().hour
    def check_status_hourly(self):
        today=datetime.datetime.now()
        if not self.value: # not turned on
            if today.hour == self.hour: # not new hour
                if self.watered_this_hour:
                    return False
                else:
                    self.watered_this_hour=True
                    return True
            else:
                self.hour=today.hour # update hour
                self.watered_this_hour=True
                return True
        return False
    def check_status_half(self):
        today=datetime.datetime.now()
        if not self.value: # not turned on
            if today.minute >= 30 and today.minute <= 39: # in timeframe
                if self.watered_this_half:
                    return False
                else:
                    self.watered_this_half=True # should go after the watering, but if fails prefer too little
                    return True
            else:
                self.watered_this_half=False
                return False
        return False
    def open_the_floodgates(self):
        self.on()
        # insert webhook ping here
        time.sleep(self.duration)
        # insert webhook ping here
        self.off()

class Queue(length=1, duration=datetime.datetime.timedelta(seconds=120)):
    def __init__(self, length, duration):
        self.length=length
        self.duration=datetime.timedelta(seconds=duration) # in seconds
        self.data=[]
        self.last_published=datetime.datetime.now() # for now
        
    def isReady(self): # if length is reached or duration since last post, True
        if len(self.data) == self.length: # length
            return True
        elif datetime.datetime.now() - self.last >= self.duration: # duration reached
            return True
        else:
            return False # not ready to be sent yet
        
    def flush():
        self.last_published=datetime.datetime.now()
        self.data=[]
        
class Camera():
    def __init__(self, elapse, iso, shutter_speed, awb_gains, res, framerate, aws_end):
        self.camera=PiCamera(resolution=res, framerate=framerate)
        self.camera.iso=iso
        self.camera.shutter_speed = self.camera.shutter_speed
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = awb_gains
        self.aws_end=aws_end
        self.elapse=elapse

def read_in_aws_keys(path_to_keys):
    with open(path_to_keys, 'r') as csvfile:
        reader=csv.DictReader(csvfile)
        key_info=[]
        for row in reader:
            key_info.append(row)
            
    MY_ACCESS_KEY_ID=key_info[0]['Access key ID']
    MY_SECRET_ACCESS_KEY=key_info[0]['Secret access key']
    MY_REGION_ID=key_info[0]['Region ID']
    
    return {'id': MY_ACCESS_KEY_ID, 'secret': MY_SECRET_ACCESS_KEY, 'region': MY_REGION_ID}

def open_s3_resource(path_to_keys, bucket_name):
    keys=read_in_aws_keys(path_to_keys)
    aws_access_key_id=keys['id']
    aws_secret_access_key=keys['secret']
    region_name=keys['region']
    s3 = boto3.resource('s3',
                          aws_access_key_id = aws_access_key_id,
                          aws_secret_access_key = aws_secret_access_key,
                          region_name = region_name
                          )
    bucket = s3.Bucket(bucket_name)
    return s3,bucket

def open_dynamodb_resource(path_to_keys, db_name, table_name):
    keys=read_in_aws_keys(path_to_keys)
    aws_access_key_id=keys['id']
    aws_secret_access_key=keys['secret']
    region_name=keys['region']
    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id = aws_access_key_id,
                              aws_secret_access_key = aws_secret_access_key,
                              region_name = region_name
                              )
    table=dynamodb.Table(table_name)
    return dynamodb,table

def publish_to_aws(queue, path_to_keys, bucket_name, db_name):
    # NEED TO CONSIDER POWER REQUIREMENTS FOR BATTERY OPERATION + SCHEDULING
    # publishes a queue to AWS
    # queue data holds its own endpoint information, with the environment holding the other data
    
    # check which resource we need - ADD IN LATER
    # needed_resource=set([q.aws_end for q in queue]))
    
    s3, bucket=open_s3_resource(path_to_keys, bucket_name)
    db, table=open_dynamodb_resource(path_to_keys, db_name)
    for q in queue:
        if q['aws_end'] == 'dynamodb':
            q.pop('aws_end', None)
            with table.batch_writer() as batch:
                batch.put_item(Item=q)
        elif q['aws_end'] == 's3':
            q.pop('aws_end', None)
            bucket.upload_file(q['image'], q['key']) # key is probably the timestamp
    return 1

def main():
    home = str(Path.home())
    output_path = os.path.join(home, 'Documents',  'probe_output.txt')
    log_file= os.path.join(home, 'Documents', 'log_file.txt')
    
    # AWS Setup and Credentials
    path_to_keys=[]
    bucket_name='project-sia'
    db_name='project-sia'
    
    atlas=AtlasI2C() # create communications bus
    
    # register probes
    poll_time=2
    queue_length=1
    
    reservoir_pump=Pumps(30, 5) # digital pin 5

    lights_long=Lights(18, 14, 20, 17) # NEED TO REMOVE THE BAD DURATION CODE ABOVE
    lights_med=Lights(18, 12, 18, 27)
    lights_short=Lights(18, 10, 16, 22)
    lighting=[lights_long, lights_med, lights_short]

    do=Probe('do', 97, atlas, poll_time, 'dynamodb')
    orp=Probe('orp', 98, atlas, poll_time, 'dynamodb')
    ph=Probe('ph', 99, atlas, poll_time,'dynamodb')
    ec=Probe('ec', 100, atlas, poll_time, 'dynamodb')
    rtd=Probe('rtd', 102, atlas, poll_time, 'dynamodb')
    co2=Probe('co2', 105, atlas, poll_time, 'dynamodb')
    camera=Camera(datetime.timedelta(hours=1))
    queue=Queue(length=queue_length)
    
    sensors=[do, orp, ph, rtd, ec, co2]
    while True:
        try:
            while True:
                for s in sensors:
                    a=s.poll()
                    item = {'sensorID': a[0], 'value': a[1], 'timestamp': a[2], 'aws_end': a[3]}
                    queue.append(item)
                    if queue.isReady():
                        if publish_to_aws(queue, path_to_keys, bucket_name, db_name): # success!
                            queue.flush()
                # how to run each camera from one computer?
                for light in lighting:
                    if light.check_status(): # if True, flip switch
                        light.flip_light()
                if reservoir_pump.check_status_hourly():
                    reservoir_pump.open_the_floodgates()
                if reservoir_pump.check_status_half():
                    reservoir_pump.open_the_floodgates()
                print('Successfully polled sensors.\nHibernating.')
        except Exception as e:
            with open (log_file, 'w') as log:
                log.write(e.message + '\t' + datetime.datetime.now() + '\n')

if __name__ == "__main__":
    # execute only if run as a script
    main()
