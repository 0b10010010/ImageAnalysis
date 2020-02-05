#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 18:32:35 2020

@author: spykat
"""

from time import sleep
from dronekit import connect, Vehicle
from TeamSpykatVehicle import TeamSKVehicle

class ReadDroneKitDataWorker(object):
    '''
        Request for SYSTEM_TIME item from the Mission Planner MAVLink and write
        to file at 100 ms interval
    '''
    def __init__(self):
        # Constructor
#        self.connectionStr =  'tcp:192.168.15.103:14550' # MP IP address
        self.connectionStr =  'tcp:192.168.0.6:14550' # test IP address
        self.gpsData = '/home/spykat/Desktop/GPSDataTargetDir/GPSData.txt'
#        self._time_unix_usec = 0
#        self._heading = 0.0
#        self._altitude = 0.0
        
#        thread = threading.Thread(target=self.readAndWriteToFile, args=())
#        thread.daemon = True
#        thread.start()
        
    def connectToVehicle(self):
        self.vehicle = connect(self.connectionStr, vehicle_class=TeamSKVehicle)
        self.vehicle.add_attribute_listener('system_time', self.readAndWriteToFile_callback)
     
    def closeVehicle(self):
        self.vehicle.close()
    
#    def system_time_callback(self, attr_name, val):
##        attr_name = 'system_time'
#        val = self.vehicle.system_time
#        
#        
#    self.vehicle.add_attribute_listener('system_time', system_time_callback)
    def readAndWriteToFile_callback(self, vehicle):
        '''
            This method will run forever in the background while GUI is running
        '''
#        self._time_unit_usec = self.vehicle.system_time.time_unix_usec
#        self._heading = self.vehicle.heading
#        self._altitude = self.vehicle.location.global_frame.alt
#        self._lat = self.vehicle
#        self._lon
#        while(True): 
        VFR_HUD = open('MPData/VFR_HUD.txt', 'a')
        VFR_HUD.write("Time(usec): {},".format(self.vehicle.system_time.time_unix_usec)  + " Altitude: {} ".format(self.vehicle.location.global_frame.alt) \
                      + "Heading: {},".format(self.vehicle.heading) + " Lat: {},".format(self.vehicle.location.global_frame.lat) + "Lon: {}\n".format(self.vehicle.location.global_frame.lon))
        