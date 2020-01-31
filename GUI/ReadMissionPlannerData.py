#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:25:25 2019

@author: Alex Kim
"""

# Use IP address of computer that's running mission planner:
# 192.168.15.#:56781/mavlink/ where # should be the respective machine's IP
# Refer to the following webpage
# https://diydrones.com/forum/topics/forwarding-telemetry-data-not-the-mavlink-stream-from-mission

import urllib.request, json, threading
from time import sleep

class ReadMPDataWorker():
    def __init__(self):    
        self.url =  "http://192.168.15.103:56781/mavlink/"
    
    def readAndWriteToFile(self):
        while(True):
            with urllib.request.urlopen(self.url) as j:
                parsedJSON = json.loads(j.read().decode("utf-8"))
                try:
                    alt = parsedJSON["VFR_HUD"]["msg"]["alt"]
                    heading = parsedJSON["VFR_HUD"]["msg"]["heading"]
                    lat = parsedJSON["GPS_RAW_INT"]["msg"]["lat"]
                    lon = parsedJSON["GPS_RAW_INT"]["msg"]["lon"]
                    time_usec = parsedJSON["GPS_RAW_INT"]["msg"]["time_usec"]
            #        airspeed = parsedJSON["VFR_HUD"]["msg"]["airspeed"]
            #        throttle = parsedJSON["VFR_HUD"]["msg"]["throttle"]
            #        roll = parsedJSON["ATTITUDE"]["msg"]["roll"]
            #        pitch = parsedJSON["ATTITUDE"]["msg"]["pitch"]
            #        target_bear= parsedJSON["NAV_CONTROLLER_OUTPUT"]["msg"]["target_bearing"]
            #        climb = parsedJSON["VFR_HUD"]["msg"]["climb"]
                except:
                    print("Beware the target bear!!!!")
                
                VFR_HUD = open('VFR_HUD.txt', 'a')
                VFR_HUD.write("Time(usec): {} ".format(time_usec)  + "Altitude: {} ".format(alt) \
                              + "Heading: {} ".format(heading) + "Lat: {} ".format(lat) + "Lon: {}\n".format(lon))
                sleep(0.1)
# run infinitely in the background on Odroid
if __name__ == '__main__':
    r = ReadMPDataWorker()
    thread = threading.Thread(target=r.readAndWriteToFile())
    thread.start()