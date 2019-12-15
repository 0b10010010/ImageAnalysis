#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 17:08:01 2019

@author: Alex Kim
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, subprocess, signal, os

class CamTrigWorker(QObject):
#    path = os.getcwd()
    
    finishedTriggering = pyqtSignal()
    finishedDetect = pyqtSignal()
    finishedCancelTrig = pyqtSignal()
    respReady = pyqtSignal('PyQt_PyObject')
    
    def __init__(self):
        super().__init__()
        self.host = 'odroid@odroid'
        self.mkdir = 'cd ~/Desktop/Capture#%d;'
        self.mkdirNum = 1
    
        # gphoto2 shell commands
        self.detectCam = 'gphoto2 --auto-detect'
        self.triggerCam = 'gphoto2 --capture-image-and-download --interval 3'
        self.stopTrig = 'gphoto2 --reset-interval'
        self.cancelTrig = signal.SIGINT
        self.result = []
    
#    process = subprocess.Popen(["ssh", "%s" % host], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    @pyqtSlot()
    def sendMkdirCmd(self):
        self.cmdMkdir = subprocess.Popen(["ssh", "{}".format(self.host), (self.mkdir%self.mkdirNum + self.triggerCam)], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#        (self.result, self.err) = self.process.communicate(bytes(self.triggerCam, 'utf-8'))
        self.mkdirNum += 1
        self.result = self.cmdMkdir.stdout.read()
#        (self.result, self.err) = self.cmdMkdir.communicate()
#        self.respReady.emit((self.result))
        
        if self.result == []:
            error = self.cmdMkdir.stderr.read()
            print(sys.stderr, "ERROR: {}".format(error.decode('utf-8')))
        else:
            print(self.result.decode('utf-8'))
#        print(self.result)
    
    @pyqtSlot()
    def sendDetCmd(self):
        self.cmdDetectCam = subprocess.Popen(["ssh", "{}".format(self.host), self.detectCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.result = self.cmdDetectCam.stdout.read()
        if self.result == []:
            error = self.cmdDetectCam.stderr.read()
            print(sys.stderr, "ERROR: {}".format(error.decode('utf-8')))
        else:
            print(self.result.decode('utf-8'))
        self.finishedDetect.emit()
            
    @pyqtSlot()
    def sendTrigCmd(self):
        self.cmdTrigCam = subprocess.Popen(["ssh", "{}".format(self.host), self.triggerCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.result = self.cmdTrigCam.stdout.read()
        if self.result == []:
            error = self.cmdTrigCam.stderr.read()
            print(sys.stderr, "ERROR: {}".format(error.decode('utf-8')))
#            self.finishedTriggering.emit(self.result)
        else:
            print(self.result.decode('utf-8'))
#            self.respReady.emit(self.result)
    
    @pyqtSlot()
    def cancelTrigCmd(self):
        os.kill(self.cmdMkdir.pid, signal.SIGTERM)
#        self.cmdMkdir.send_signal(self.cancelTrig)
#        self.finishedTriggering.emit()
        
#        subprocess.Popen(["ssh", "%s" % self.host, self.cancelTrig], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
#        self.cmdMkdir.send_signal(self.cancelTrig)
#        self.finishedCancelTrig.emit()
#        self.process.communicate((self.cancelTrig))

#        print('here')
#        self.cancelTrigCam = subprocess.Popen(["ssh", "%s" % self.host], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        self.cancelTrigCam.send_signal(self.cancelTrig)
#        if self.result == []:
#            error = self.cancelTrigCam.stderr.readlines()
#            print(sys.stderr, "ERROR: %s" % error)
#        else:
#            print(self.result)
#        self.finishedCancelTrig.emit()
#        self.finishedTriggering.emit()