#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 18:32:35 2020

@author: Alex Kim
"""


from time import sleep
from threading import Thread, currentThread
from dronekit import connect
from TeamSpykatVehicle import TeamSKVehicle
import threading

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
class DroneKitWorker(QObject):
    
    finishedConnecting = pyqtSignal(int)
    status = 0
    
    def __init__(self):
        super().__init__()
        self.connectionStr = 'tcp:192.168.15.103:14550' # test IP address
        
    @pyqtSlot()
    def connectVehicle(self):
        self.vehicle = connect(self.connectionStr, vehicle_class=TeamSKVehicle)
        self.status = 1
        print(" Autopilot Firmware version: %s" % self.vehicle.version)
        self.finishedConnecting.emit(self.status)
        self.vehicle.add_attribute_listener('system_time', self.readAndWriteToFile_callback)
        while True:
            pass

    def readAndWriteToFile_callback(self, attr_name, val, vehicle):
        '''
            This method will run forever in the background while GUI is running
            0.5 seconds interval between updates. (2 Hz)
        '''
        # print(attr_name, val)
        VFR_HUD = open('MPData/VFR_HUD.txt', 'a')
        VFR_HUD.write("Time(usec):{},".format(self.vehicle.system_time.time_unix_usec)  + "Altitude:{},".format(self.vehicle.location.global_frame.alt) \
                      + "Heading:{},".format(self.vehicle.heading) + "Lat:{},".format(self.vehicle.location.global_frame.lat) + "Lon:{}\n".format(self.vehicle.location.global_frame.lon))
        
        # self.attributeListener_thread = Thread(target=self.addAttributeListener, args = ())
        # self.attributeListener_thread.daemon = True
        # self.attributeListener_thread.start()
        # self.finishedConnecting.emit(self.status)
        
    # def addAttributeListener(self):
    #     # self.attributeListener_thread = currentThread()
    #     self.vehicle.add_attribute_listener('system_time', self.readAndWriteToFile_callback)
    #     while True:
    #         pass
        # while getattr(self.attributeListener_thread, "do_run", True):
        #     pass
        # print('MP logging stopped')
        
# vehicle.wait_ready('autopilot_version', timeout=180)
# Get all vehicle attributes (state)
# print("\nGet all vehicle attribute values:")
# print(" Autopilot Firmware version: %s" % vehicle.version)

        
# vehicle.add_attribute_listener('system_time', readAndWriteToFile_callback)
    @pyqtSlot()
    def closeVehicle(self):
        self.vehicle.close()
        # self.attributeListener_thread.do_run = False
        # self.attributeListener_thread.join()

# # from time import sleep
# from dronekit import connect
# from TeamSpykatVehicle import TeamSKVehicle

# connectionStr =  'tcp:192.168.0.6:14550' # test IP address
# vehicle = connect(connectionStr, vehicle_class=TeamSKVehicle)
# #vehicle.wait_ready('autopilot_version', timeout=180)
# # Get all vehicle attributes (state)
# print("\nGet all vehicle attribute values:")
# print(" Autopilot Firmware version: %s" % vehicle.version)

# def readAndWriteToFile_callback(self, attr_name, val):
#     '''
#         This method will run forever in the background while GUI is running.
#         Lines have 0.5 seconds interval between updates. (2 Hz)
#     '''
#     VFR_HUD = open('FlightData/VFR_HUD.txt', 'a')
#     VFR_HUD.write("Time(usec):{},".format(vehicle.system_time.time_unix_usec) + "Altitude:{}".format(vehicle.location.global_frame.alt) \
#                   + "Heading:{},".format(vehicle.heading) + "Lat:{},".format(vehicle.location.global_frame.lat) + "Lon:{}\n".format(vehicle.location.global_frame.lon))
    
# vehicle.add_attribute_listener('system_time', readAndWriteToFile_callback)

# #sleep(600) # write to file for 10 minutes then exit

# while(True):
#     pass
# vehicle.close()