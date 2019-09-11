#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 17:08:01 2019

@author: Alex Kim
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, subprocess, signal, os

class camTrigWorker(QObject):
    path = os.getcwd()
    
    finishedTriggering = pyqtSignal()
    finishedDetect = pyqtSignal()
    finishedCancelTrig = pyqtSignal()
    respReady = pyqtSignal(str)
    
    host = "odroid@odroid"        
    # gphoto2 shell commands
    detectCam = 'gphoto2 --auto-detect'
    triggerCam = 'gphoto2 --capture-image-and-download --interval 3'
    cancelTrig = signal.SIGINT
    result = []
    
    @pyqtSlot()
    def sendDetCmd(self):
        self.cmdDetectCam = subprocess.Popen(["ssh", "%s" % self.host, self.detectCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.result = self.cmdDetectCam.stdout.readlines()
        if self.result == []:
            error = self.cmdDetectCam.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
        else:
            print(self.result)
#        self.finishedDetect.emit()
            
    @pyqtSlot()
    def sendTrigCmd(self):
        self.cmdTrigCam = subprocess.Popen(["ssh", "%s" % self.host, self.triggerCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.result = self.cmdTrigCam.stdout.readlines()
        if self.result == []:
            error = self.cmdTrigCam.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
        else:
            print(self.result)
#        self.respReady.emit(self.result)
#        self.finishedTriggering.emit()
    
    @pyqtSlot()
    def cancelTrigCmd(self):
        self.cancelTrigCam = subprocess.Popen(["ssh", "%s" % self.host], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.cancelTrigCam.send_signal(self.cancelTrig)
        if self.result == []:
            error = self.cancelTrigCam.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
        else:
            print(self.result)
#        self.finishedCancelTrig.emit()