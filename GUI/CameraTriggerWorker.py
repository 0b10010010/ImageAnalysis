#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 17:08:01 2019

@author: Alex Kim
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, subprocess, signal, os

class CamTrigWorker(QObject):

    finishedTriggering = pyqtSignal()
    finishedDetect = pyqtSignal()
    finishedCancelTrig = pyqtSignal()
    respReady = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super().__init__()
        self.host = 'odroid@192.168.15.99'
        self.dir = 'cd ~/Desktop/Capture#%d;'
        self.dirNum = 1
    
        # gphoto2 shell commands
        self.detectCam = 'gphoto2 --auto-detect'
        self.triggerCam = 'gphoto2 --capture-image-and-download --interval 3'
        self.stopTrig = 'gphoto2 --reset-interval'
        self.cancelTrig = signal.SIGINT
        self.result = []
    
    @pyqtSlot()
    def sendMkdirCmd(self):
        self.cmdMkdir = subprocess.Popen(["ssh", "{}".format(self.host), (self.dir%self.dirNum + self.triggerCam)], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.dirNum += 1        
        for line in iter(self.cmdMkdir.stdout.readline, b''):
            sys.stdout.write(line)
    
    @pyqtSlot()
    def sendDetCmd(self):
        self.cmdDetectCam = subprocess.Popen(["ssh", "{}".format(self.host), self.detectCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(self.cmdDetectCam.stdout.readline, b''):
            sys.stdout.write(line)
#        self.result = self.cmdDetectCam.stdout.read()
#        if self.result == []:
#            error = self.cmdDetectCam.stderr.read()
#            print(sys.stderr, "ERROR: {}".format(error.decode('utf-8')))
#        else:
#            print(self.result.decode('utf-8'))
        self.finishedDetect.emit()
            
    @pyqtSlot()
    def sendTrigCmd(self):
        self.cmdTrigCam = subprocess.Popen(["ssh", "{}".format(self.host), self.triggerCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(self.cmdTrigCam.stdout.readline, b''):
            sys.stdout.write(line)
    
    @pyqtSlot()
    def cancelTrigCmd(self):
        os.kill(self.cmdMkdir.pid, signal.SIGTERM)