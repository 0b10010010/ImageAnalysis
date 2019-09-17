#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 17:08:01 2019

@author: Alex Kim
"""

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, subprocess, signal, os

class CamTrigWorker(QObject):
    path = os.getcwd()
    
    finishedTriggering = pyqtSignal()
    finishedDetect = pyqtSignal()
    finishedCancelTrig = pyqtSignal()
    respReady = pyqtSignal('PyQt_PyObject')
    
    host = 'odroid@odroid'
    mkdir = 'cd ~/Desktop/Capture#%d;'
    mkdirNum = 1

    # gphoto2 shell commands
    detectCam = 'gphoto2 --auto-detect'
    triggerCam = 'gphoto2 --capture-image-and-download --interval 3'
    stopTrig = 'gphoto2 --reset-interval'
    cancelTrig = signal.SIGINT
    result = []
    
#    process = subprocess.Popen(["ssh", "%s" % host], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    @pyqtSlot()
    def sendMkdirCmd(self):
        self.cmdMkdir = subprocess.Popen(["ssh", "%s" % self.host, (self.mkdir%self.mkdirNum + self.triggerCam)], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        (self.result, self.err) = self.process.communicate(bytes(self.triggerCam, 'utf-8'))
        self.mkdirNum += 1
        self.result = self.cmdMkdir.stdout.readlines()
#        (self.result, self.err) = self.cmdMkdir.communicate()
#        self.respReady.emit((self.result))
        
        if self.result == []:
            error = self.cmdMkdir.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
        else:
            print(self.result)
#        print(self.result)
    
    @pyqtSlot()
    def sendDetCmd(self):
        self.cmdDetectCam = subprocess.Popen(["ssh", "%s" % self.host, self.detectCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.result = self.cmdDetectCam.stdout.readlines()
        if self.result == []:
            error = self.cmdDetectCam.stderr.readlines()
            print(sys.stderr, "ERROR: %s" % error)
        else:
            print(self.result)
        self.finishedDetect.emit()
            
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