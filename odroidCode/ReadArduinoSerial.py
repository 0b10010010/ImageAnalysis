#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 20:08:19 2019

@author: Alex Kim

This python script should run on the onboard computer
"""

import serial, threading

class ReadArduinoSerialWorker():
    '''
        Read serial data from the Arduino onboard via USB and save to a text
        file    
    '''
    def __init__(self):
        self.port = '/dev/ttyUSB1' #TODO: Change this port accordingly
        self.baud = 115200
        self.msg = []
        self.arduino = serial.Serial(self.port, self.baud)
    
    def readSerialAndWriteToFile(self):
        #TODO: maybe wait for a sentence to be buffered?
        try:
            while (True):
                if self.arduino.inWaiting():
                    self.msg = self.arduino.readline()
                    self.GPSData = open('GPSData.txt', 'a')
            #        self.GPSData = open('/home/spycat/Desktop/image-analysis/ProcessedTargets/GPSData.txt', 'a') # TODO: save to shared directory where images will be
                    self.GPSData.write(self.msg.decode('utf-8'))
    #        self.GPSData.close()
        except:
            pass
            
# run infinitely in the background on Odroid
if __name__ == '__main__':
    r = ReadArduinoSerialWorker()
    r.readSerialAndWriteToFile()
    # TODO: threading might not be necessary when running on terminal as a background
    #       processing
#    thread = threading.Thread(target=r.readSerialAndWriteToFile())
#    thread.start()