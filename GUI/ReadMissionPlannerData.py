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

import urllib.request, json, threading
from time import sleep

class ReadMPDataWorker(object):
    '''
        Request for VFR_HUD items from the Mission Planner and write to file at
        100 ms interval
    '''
    def __init__(self):
        # Constructor
        self.url =  'http://192.168.15.103:56781/mavlink/' # MP IP address
        self.gpsData = '/home/spykat/Desktop/GPSDataTargetDir/GPSData.txt'
        self._time_usec = 0
        self._heading = 0.0
        self._altitude = 0.0
        
        thread = threading.Thread(target=self.readAndWriteToFile, args=())
        thread.daemon = True
        thread.start()
    
    def readAndWriteToFile(self):
        '''
            This method will run forever in the background while GUI is running
        '''
        while(True):
            with urllib.request.urlopen(self.url) as j:
                parsedJSON = json.loads(j.read().decode("utf-8"))
                try:
                    time_usec = parsedJSON['GPS_RAW_INT']['msg']['time_usec']
                    alt       = parsedJSON['VFR_HUD']['msg']['alt']
                    heading   = parsedJSON['VFR_HUD']['msg']['heading']
                    lat       = parsedJSON['GPS_RAW_INT']['msg']['lat']
                    lon       = parsedJSON['GPS_RAW_INT']['msg']['lon']
            #        roll = parsedJSON["ATTITUDE"]["msg"]["roll"]
            #        pitch = parsedJSON["ATTITUDE"]["msg"]["pitch"]
            #        climb = parsedJSON["VFR_HUD"]["msg"]["climb"]
                    self._time_usec = time_usec
                    self._heading = heading
                    self._altitude = alt
                    VFR_HUD = open('MPData/VFR_HUD.txt', 'a')
                    VFR_HUD.write("Time(usec): {},".format(time_usec)  + " Altitude: {} ".format(alt) \
                                  + "Heading: {},".format(heading) + " Lat: {},".format(lat) + "Lon: {}\n".format(lon))            
                except:
                    print('Exception')
                    
                sleep(0.1) # delay 100 ms

## run infinitely in the background on Odroid
#if __name__ == '__main__':
#    r = ReadMPDataWorker()
#    thread = threading.Thread(target=r.readAndWriteToFile())
#    thread.start()