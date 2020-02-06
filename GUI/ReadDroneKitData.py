#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 18:32:35 2020

@author: Alex Kim
"""

# from time import sleep
from dronekit import connect
from TeamSpykatVehicle import TeamSKVehicle

connectionStr =  'tcp:192.168.0.6:14550' # test IP address
vehicle = connect(connectionStr, vehicle_class=TeamSKVehicle)
#vehicle.wait_ready('autopilot_version', timeout=180)
# Get all vehicle attributes (state)
print("\nGet all vehicle attribute values:")
print(" Autopilot Firmware version: %s" % vehicle.version)

def readAndWriteToFile_callback(self, attr_name, val):
    '''
        This method will run forever in the background while GUI is running.
        Lines have 0.5 seconds interval between updates. (2 Hz)
    '''
    VFR_HUD = open('FlightData/VFR_HUD.txt', 'a')
    VFR_HUD.write("Time(usec):{},".format(vehicle.system_time.time_unix_usec) + "Altitude:{}".format(vehicle.location.global_frame.alt) \
                  + "Heading:{},".format(vehicle.heading) + "Lat:{},".format(vehicle.location.global_frame.lat) + "Lon:{}\n".format(vehicle.location.global_frame.lon))
    
vehicle.add_attribute_listener('system_time', readAndWriteToFile_callback)

#sleep(600) # write to file for 10 minutes then exit

while(True):
    pass
vehicle.close()