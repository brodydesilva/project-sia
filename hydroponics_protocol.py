# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 18:11:19 2018

@author: 1brod
"""

# read in configuration from file
    # lights, pumps, etc.

class switch(id=-1):
    # Any output device that has a pin number
    def __init__(self):
        self.id=id
        
class sensor(id=-1):
    # any input device (sensor)
    def __init__(self):
        self.id=id
    def poll():
        pass

class lights(switch, duration=0, start=):
    def __init__(self):
        super().__init__()
        self.duration=duration
    def check_status():
        # add in LDR circuit pin check for low / high voltage
        # make this a digital status instead of analog voltage readings
        pass
    def activate():
        pass
    def deactivate():
        pass

def nutrient_pump():
    pass
def ph():
    pass
def ec():
    pass
def water_level():
    pass
def orp():
    pass
def do():
    # 
    pass
def co2():
    # on startup, needs to wait 10 minutes for thermal equilibrium
    pass
def bilge_pump():
    pass

def export_info():
    # inputs
    # outputs
    pass

def main():
    
    # initialize
    # senors, lighting schedule, pumps, sensors
    
    initialize('all')
    take_initial_readings('all')
    
    pass

if __name__ == "__main__":
    # execute only if run as a script
    main()