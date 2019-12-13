#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 20:08:19 2019

@author: Alex Kim

This python script should run on the onboard computer
"""

import serial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class ReadArduinoSerial(QObject):
    finished = pyqtSignal()
    port = '/dev/ttyUSB1'
    baud = 115200
    msg  = ''
    arduino = serial.Serial(port, baud, timeout=5)
    
    @pyqtSlot()
    def readSerial(self):
        # maybe wait for a sentence to be buffered
        
        msg = self.arduino.read(self.arduino.in_waiting())
        
#        GPSData = open('GPSData.txt', 'w')
#        GPSData.write(msg + '\n')
        print(msg)
        
while (1):
    ReadArduinoSerial.msg()