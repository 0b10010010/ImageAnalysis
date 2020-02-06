#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:25:25 2019

@author: Alex Kim

Use IP address of computer that's running mission planner:
192.168.15.#:56781/mavlink/ where # should be the respective machine's IP
Refer to the following webpage
https://diydrones.com/forum/topics/forwarding-telemetry-data-not-the-mavlink-stream-from-mission

This python script should run on the GCS computer
"""

import numpy as np
from datetime import datetime, timezone

class ReadMPDataWorker(object):
    '''
        Read from stored GPSData text file from OBC and match the GPS time with
        MPData time to return heading and altitude information to geolocate
    '''
    def __init__(self):
        self.MPData = 'FlightData/VFR_HUD.txt'
        self.GPSData = 'FlightData/GPSData.txt'
        self.MPMavLinkData = [] # Data from MAVLink received from AutoPilot's MP
        self.timeDiff = 500000 # given time difference limit for matching trigger time # TODO: find this limit
        self.lineNumber = 1
        
    def readFromGPSData(self, imgNumber):
        with open(self.GPSData) as file:
            for line in file:
                if (self.lineNumber == imgNumber+1): # imgNumber index starts at 0
                    lists = [lines.strip() for lines in line.split(',')]
                    timeValue = lists[1][5:]
                    dateTime = datetime.strptime(timeValue[:-3], '%Y/%m/%d %H:%M:%S.%f')           # convert to usec resolution
                    timeStamp = dateTime.replace(tzinfo=timezone.utc).timestamp()*1000000 # time in epoch (usec)
                    self.MPMavLinkData.append(self.readFromMPData(timeStamp)) # Data matching GPS time from MP                
                    altitude = self.readFromMPData(timeStamp)[1]
                    heading = self.readFromMPData(timeStamp)[2]
                    lat = self.readFromMPData(timeStamp)[3]
                    lon = self.readFromMPData(timeStamp)[4]
                    latGPS = lists[2] # have a copy of GPSData coordinates
                    lonGPS = lists[3]
                    # TODO: compare GPSData lat/lon with latGPS/lonGPS
                    # self.altitude.append(self.readFromMPData(timeStamp)[1])
                    # self.heading.append(self.readFromMPData(timeStamp)[2])
                    # self.latMP.append(self.readFromMPData(timeStamp)[3])
                    # self.lonMP.append(self.readFromMPData(timeStamp)[4])
                    return altitude, heading, lat, lon
                self.lineNumber += 1
    
    def readFromMPData(self, targetTime):
        '''
            with the input of targetTime from GUI program which is the time of
            trigger, find all data from that specific time frame.
        '''
        with open(self.MPData) as file:
            lineNumber = 1
            for line in file:
                lists = [lines.strip() for lines in line.split(',')]
                print(lists)
                key, value = lists[0].split(':')
                lineNumber += 1
                if (np.abs(int(value)-targetTime) < self.timeDiff): # 500000 is 500ms difference
                    return lists

# mp = ReadMPDataWorker()
# mp.readFromMPData(12312312314)
# # TODO: each list items can be accessed by 
# key,value = mp.readFromMPData(12312312314)[4].split(':')
# print(key, value)


# import urllib.request, json, threading
# from time import sleep

# class ReadMPDataWorker(object):
#     '''
#         Request for VFR_HUD items from the Mission Planner and write to file at
#         100 ms interval
#     '''
#     def __init__(self):
#         # Constructor
#         self.url =  'http://192.168.15.103:56781/mavlink/' # MP IP address
#         self.gpsData = '/home/spykat/Desktop/GPSDataTargetDir/GPSData.txt'
#         self._time_usec = 0
#         self._heading = 0.0
#         self._altitude = 0.0
        
#         thread = threading.Thread(target=self.readAndWriteToFile, args=())
#         thread.daemon = True
#         thread.start()
    
#     def readAndWriteToFile(self):
#         '''
#             This method will run forever in the background while GUI is running
#         '''
#         while(True):
#             with urllib.request.urlopen(self.url) as j:
#                 parsedJSON = json.loads(j.read().decode("utf-8"))
#                 try:
#                     time_usec = parsedJSON['GPS_RAW_INT']['msg']['time_usec']
#                     alt       = parsedJSON['VFR_HUD']['msg']['alt']
#                     heading   = parsedJSON['VFR_HUD']['msg']['heading']
#                     lat       = parsedJSON['GPS_RAW_INT']['msg']['lat']
#                     lon       = parsedJSON['GPS_RAW_INT']['msg']['lon']
#             #        roll = parsedJSON["ATTITUDE"]["msg"]["roll"]
#             #        pitch = parsedJSON["ATTITUDE"]["msg"]["pitch"]
#             #        climb = parsedJSON["VFR_HUD"]["msg"]["climb"]
#                     self._time_usec = time_usec
#                     self._heading = heading
#                     self._altitude = alt
#                     VFR_HUD = open('MPData/VFR_HUD.txt', 'a')
#                     VFR_HUD.write("Time(usec): {},".format(time_usec)  + " Altitude: {} ".format(alt) \
#                                   + "Heading: {},".format(heading) + " Lat: {},".format(lat) + "Lon: {}\n".format(lon))            
#                 except:
#                     print('Exception')
                    
#                 sleep(0.1) # delay 100 ms

## run infinitely in the background on Odroid
#if __name__ == '__main__':
#    r = ReadMPDataWorker()
#    thread = threading.Thread(target=r.readAndWriteToFile())
#    thread.start()