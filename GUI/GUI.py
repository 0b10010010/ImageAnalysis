#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 12:49:01 2019

@author: Alex Kim
"""

import sys, platform, getEXIF, CamTrigWorker
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QLineEdit, 
                             QVBoxLayout, QAction, QSizePolicy, QHBoxLayout,
                             QGridLayout, QShortcut, QGraphicsView, QLabel,
                              QFrame, QToolButton, QMessageBox)
from PyQt5.QtCore import pyqtSlot, Qt, QThread, QTimer, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtGui import QPixmap, QKeySequence, QIcon
from PhotoViewer import PhotoViewer
# TODO: using EXIF orientation number rotate the target image

###############################################################################
# OBC: Onboard computer (Odroid XU4)
# GCS: Ground Control Station (Image Analysis and Mission Planner PC)
###############################################################################

'''
Basic application workflow:
    GUI runs on the GCS computer.
    Camera control commands are sent from GCS to OBC over 5GHz
    Pictures will be taken at three second interval and save to shared directory
    between the air and ground.
'''

###############################################################################
###############################################################################
###############################################################################
# TODO: Read from GPSData.txt on OBC
#class ReadTelemetryLog():
#    def __init__(self):
#        self.dict = {}
#        self.infoByFrame = []
#        self.lattitudes = []
#        self.longitudes = []
#        self.logFilePath = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/flight.txt'
#        
#    def readAttitude(self):
#        with open(self.logFilePath, 'rt') as in_file:
#            for line in in_file:
##                self.infoByFrame.append(line.split(','))
#                self.infoByFrame.append(line[39::])
##                self.longitudes.append(line.)
##        print(self.infoByFrame)
#        for lines in self.infoByFrame:
#            self.lattitudes.append(lines[76:86].split(',')[0])
#        print(self.lattitudes[0])
#        
#    def transform():
#        pass
    
###############################################################################
###############################################################################
###############################################################################            
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        '''
            MainWindow Object to put together GUI layouts and its Widgets
        '''
#        super(MainWindow, self).__init__(parent)
        super().__init__()
        self.viewer = PhotoViewer(self)
#        self.readLog = ReadTelemetryLog()
        
        self.flightNumber = 0
        
        # Add Window Title
        self.setWindowTitle('Team Spycat Image Analysis 1.0')
        
        # Add an Icon
        self.setWindowIcon(QIcon('airport.svg'))
        
        #######################################################################
        # ADD SHORTCUTS
        #######################################################################
        self.shortClose = QShortcut(QKeySequence('Ctrl+w'), self)
        self.shortClose.activated.connect(self.close)

        #######################################################################
        # ADD MENU ITEMS
        #######################################################################
        # Create the File menu
        self.menuFile = self.menuBar().addMenu("&File")
        self.actionQuit = QAction("&Quit", self)
        self.actionQuit.triggered.connect(self.close)
        self.menuFile.addActions([self.actionQuit])
        
        # Create the Help menu
        self.menuHelp = self.menuBar().addMenu("&Help")
        self.actionAbout = QAction("&About",self)
        self.actionAbout.triggered.connect(self.about)
        self.menuHelp.addActions([self.actionAbout])

        #######################################################################
        # CREATE CENTRAL WIDGET
        #######################################################################

        # Info Bar ############################################################        
        # 'Detect Camera' button
        self.btnDetectCam = QToolButton(self)
        toolButtonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btnDetectCam.setSizePolicy(toolButtonSizePolicy)
        self.btnDetectCam.setText('Detect Camera')
        self.btnDetectCam.clicked.connect(self.sendDetectCameraCommand)

        # 'Start Triggering Camera' button
        self.btnCamTrig = QToolButton(self)
        self.btnCamTrig.setCheckable(True)
        self.btnCamTrig.setStyleSheet("QToolButton {background-color: red}"
                                      "QToolButton:checked {background-color: green}")
        self.btnCamTrig.setSizePolicy(toolButtonSizePolicy)
        self.btnCamTrig.setText('Start Triggering Camera')
        self.btnCamTrig.clicked.connect(self.btnCamTrigHandler)

        # TODO: when trigger button gets pressed create folder and put images there
        
        # TODO: add more buttons to abort camera trigger or other linux cmds
        
        # 'Load image' button
        self.btnLoad = QToolButton(self)
        self.btnLoad.setSizePolicy(toolButtonSizePolicy)
        self.btnLoad.setText('Load Image')
        self.btnLoad.clicked.connect(self.loadImage)
        
        # Display Information
        self.loadedImg = QLabel('<b>Frame #:</b>')                          
        self.loadedImg.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.loadedImg.setFixedWidth(100)
        self.loadedImgNumber = QLineEdit(self)
        self.loadedImgNumber.setReadOnly(True)
        self.loadedImgNumber.setFixedWidth(100)
        self.loadedImgNumber.setText('%d' %self.viewer.imgNumber)
        self.viewer.keyPressed.connect(self.keyPress)

        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QLabel(self)
        self.btnPixInfo.setText('<b>Pixel Info:</b>')
        self.btnPixInfo.setStyleSheet("QLabel { color: rgb(255,255,255)}") 
#        self.btnPixInfo.setCheckable(True)
#        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.editPixInfo.setFixedWidth(100)
        self.viewer.photoClicked.connect(self.photoClick)
        
        # For users to input characteristics of targets (letter, shape, color)
        self.userInput = QLabel(self)
        self.userInput.setText('<b>Alphanumeric:</b>')
        self.userInput.setStyleSheet("QLabel { color: rgb(255,255,255) }")
        self.editUserInput = QLineEdit(self)
        self.editUserInput.setFixedWidth(100)
        self.userInputAlphanumericColor = QLabel(self)
        self.userInputAlphanumericColor.setText('<b>Alphanumeric Color:</b>')
        self.userInputAlphanumericColor.setStyleSheet("QLabel { color: rgb(255,255,255) }")
        self.editUserInputAlphanumericColor = QLineEdit(self)
        self.editUserInputAlphanumericColor.setFixedWidth(100)
        self.userInputShape = QLabel(self)
        self.userInputShape.setText('<b>Shape:</b>')
        self.userInputShape.setStyleSheet("QLabel { color: rgb(255,255,255) }") 
        self.editUserInputShape = QLineEdit(self)
        self.editUserInputShape.setFixedWidth(100)
        self.userInputShapeColor = QLabel(self)
        self.userInputShapeColor.setText('<b>Shape Color:</b>')
        self.userInputShapeColor.setStyleSheet("QLabel { color: rgb(255,255,255) }")
        self.editUserInputShapeColor = QLineEdit(self)
        self.editUserInputShapeColor.setFixedWidth(100)
        self.userInputOrientation = QLabel(self)
        self.userInputOrientation.setText('<b>Orientation:</b>')
        self.userInputOrientation.setStyleSheet("QLabel { color: rgb(255,255,255) }")
        self.editUserInputOrientation = QLineEdit(self)
        self.editUserInputOrientation.setFixedWidth(100)
        
        # For image processing
        self.cropImage = QToolButton(self)
        self.cropImage.setSizePolicy(toolButtonSizePolicy)
        self.cropImage.setText('Crop and Process')
        self.cropImage.clicked.connect(self.imageCrop)
#        self.cropImage.clicked.connect(self.readLog.transform)
        
        # Display VFR HUD Items
        self.latitude = QLabel('<b>Latitude:</b>')
        self.latitude.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.latitude.setFixedWidth(100)
        self.latitudeValue = QLineEdit(self)
        self.latitudeValue.setReadOnly(True)
        self.latitudeValue.setFixedWidth(100)
        self.latitudeValue.setText('{}'.format(self.viewer.imgNumber))
        self.longitude = QLabel('<b>Longitude:</b>')
        self.longitude.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.longitude.setFixedWidth(100)
        self.longitudeValue = QLineEdit(self)
        self.longitudeValue.setReadOnly(True)
        self.longitudeValue.setFixedWidth(100)
        self.longitudeValue.setText('{}'.format(self.viewer.imgNumber))        
        
        # Display the last processed target image
        self.processedTargetLabel = QLabel(self)
        self.processedTargetLabel.setFrameShape(QFrame.Panel)
        self.processedTargetLabel.setFrameShadow(QFrame.Sunken)
        self.processedTargetLabel.setText('<b>Previous Target</b>')
        self.processedTargetLabel.setStyleSheet("QLabel { color: rgb(255,255,255) }")
        self.processedTargetLabel.setStyleSheet("QLabel { background-color: rgb(167,167,167) }")
        self.processedTargetLabel.setAlignment(Qt.AlignCenter)
        self.processedTarget = QLabel(self)
        self.processedTarget.resize(200, 200)
        self.processedTarget.setStyleSheet("QLabel { background-color : rgb(209,209,209) }")
        self.viewer.imgReady.connect(self.showProcessedTarget)
        
        # Draw a line between the label and image
        spacerLine = QFrame()
        spacerLine.setFrameShape(QFrame.HLine)
        spacerLine.setFrameShadow(QFrame.Sunken)
        spacerLine.setLineWidth(1)
        
        #######################################################################
        # LAYOUTS
        #######################################################################
        # Processed target layout
        Target = QVBoxLayout()
        Target.addWidget(spacerLine)
        Target.addWidget(self.processedTargetLabel)
        Target.addWidget(self.processedTarget)
        Target.setAlignment(Qt.AlignCenter)
        Target.setAlignment(Qt.AlignBaseline)
        Target.addStretch(1)
        
        # Image layout
        Imglayout = QHBoxLayout()
        Imglayout.addWidget(self.viewer)

        # Image Information Grid
        ImgInfo = QGridLayout()
        ImgInfo.addWidget(self.loadedImg, 0, 0)
        ImgInfo.addWidget(self.loadedImgNumber, 0, 1)
        ImgInfo.addWidget(self.btnPixInfo, 1, 0)
        ImgInfo.addWidget(self.editPixInfo, 1, 1)
        ImgInfo.addWidget(self.userInput, 2, 0)
        ImgInfo.addWidget(self.editUserInput, 2, 1)
        ImgInfo.addWidget(self.userInputAlphanumericColor, 3, 0)
        ImgInfo.addWidget(self.editUserInputAlphanumericColor, 3, 1)        
        ImgInfo.addWidget(self.userInputShape, 4, 0)
        ImgInfo.addWidget(self.editUserInputShape, 4, 1)
        ImgInfo.addWidget(self.userInputShapeColor, 5, 0)
        ImgInfo.addWidget(self.editUserInputShapeColor, 5, 1)
        ImgInfo.addWidget(self.userInputOrientation, 6, 0)
        ImgInfo.addWidget(self.editUserInputOrientation, 6, 1)
        
        # VFR HUD Information Grid
        VFR_HUD = QGridLayout()
        VFR_HUD.addWidget(self.latitude, 0, 0)
        VFR_HUD.addWidget(self.latitudeValue, 0, 1)
        VFR_HUD.addWidget(self.longitude, 1, 0)
        VFR_HUD.addWidget(self.longitudeValue, 1, 1)
        VFR_HUD.addWidget(self.userInput, 2, 0)
        VFR_HUD.addWidget(self.editUserInput, 2, 1)
        VFR_HUD.addWidget(self.userInputAlphanumericColor, 3, 0)
        VFR_HUD.addWidget(self.editUserInputAlphanumericColor, 3, 1)        

        # Buttons layout
        Btnlayout = QVBoxLayout()
        Btnlayout.addWidget(self.btnDetectCam)
        Btnlayout.addWidget(self.btnCamTrig)
        Btnlayout.addWidget(self.btnLoad)
        Btnlayout.addLayout(ImgInfo)
        Btnlayout.addWidget(self.cropImage)
        Btnlayout.addLayout(VFR_HUD)
        Btnlayout.addStretch(1)
        # Add the last processed target image
        Btnlayout.addLayout(Target)
        
        # Final GUI layout
        GUILayout = QHBoxLayout()
        GUILayout.addLayout(Imglayout)
        GUILayout.addLayout(Btnlayout)
        
        self.widget = QDialog()
        self.widget.setLayout(GUILayout)
        self.setCentralWidget(self.widget)
        
        #######################################################################
        # THREADING
        #######################################################################
        # QTimer for updating image directory with new images taken
        self.timer = QTimer(self)
        self.timer.setInterval(3000) # update interval in ms (3 sec)
        self.timer.timeout.connect(self.updateImgDir)

        # Instantiate Worker Objects
        self.sendLinuxCmd = CamTrigWorker.CamTrigWorker()
        self.sendLinuxCmd2 = CamTrigWorker.CamTrigWorker()
        
        # Instantiate Thread Objects
        self.sendLinuxCmd_thread_startCamTrig = QThread()
        self.sendLinuxCmd_thread_detectCam = QThread()
        
        # Move Worker Objs to Thread
        self.sendLinuxCmd.moveToThread(self.sendLinuxCmd_thread_startCamTrig)
        self.sendLinuxCmd2.moveToThread(self.sendLinuxCmd_thread_detectCam)
        
        # Connect signals when threads start
        self.sendLinuxCmd_thread_startCamTrig.started.connect(self.sendLinuxCmd.sendMkdirCmd)
        self.sendLinuxCmd_thread_detectCam.started.connect(self.sendLinuxCmd2.sendDetCmd)
        
#        self.sendLinuxCmd.respReady.connect(self.printStatus)
        
    ###########################################################################
    # Member Methods
    ###########################################################################  
    def start(self):
        # start QTimer thread for updating image directory
        self.timer.start()
        # use stop() to stop
#        self.timer.stop()

    @pyqtSlot()
    def updateImgDir(self):
        self.viewer.updateImgDirectory()
        
    @pyqtSlot()
    def sendDetectCameraCommand(self):
        self.sendLinuxCmd_thread_detectCam.start()
    
    @pyqtSlot()
    def btnCamTrigHandler(self):
        if self.btnCamTrig.isChecked():
            self.btnCamTrig.setText('Cancel Triggering Camera')
            self.sendLinuxCmd_thread_startCamTrig.start()
        else:
            self.btnCamTrig.setText('Start Triggering Camera')
            self.sendLinuxCmd.cancelTrigCmd()
            self.sendLinuxCmd.finishedTriggering.connect(self.sendLinuxCmd_thread_startCamTrig.quit)
            
#    # TODO: figure out if there's a way to print triggering feedback from OBC
#    @pyqtSlot('PyQt_PyObject')
#    def printStatus(self, status):
#        print(status)

#    def pixInfo(self): # TODO: methods to handle EXIF processing and calculations
#        self.viewer.toggleDragMode()
#        print(self.viewer.getExif())
#        print('Frame #: %d' % self.viewer.imgNumber)
#        self.readLog.readAttitude()
        
    def keyPress(self, imgNumber):
        self.loadedImgNumber.setText('{}'.format(imgNumber))

    def photoClick(self, pos):
        self.viewer.toggleDragMode()
        if self.viewer.dragMode()  == QGraphicsView.NoDrag:
            self.editPixInfo.setText('{0:.0f}, {1:.0f}'.format(pos.x(),pos.y()))
            self.viewer.toggleDragMode()
            
    def imageCrop(self, pos):
        getPixel = self.editPixInfo.text().split(', ') # pixel location of clicked target
#        getEXIF.getExif(self.viewer.imgPath, self.viewer.imgList, self.viewer.imgNumber, getPixel[0], getPixel[1]) #TODO: fix the index out of range error
        self.getUserInputInfo()
        self.viewer.saveCropEvent()
        
    def getUserInputInfo(self):
        self.getAlphanumeric = self.editUserInput.text()
        self.getAlphanumericColor = self.editUserInputAlphanumericColor.text()
        self.getShape = self.editUserInputShape.text()
        self.getShapeColor = self.editUserInputShapeColor.text()
        self.getOrientation = self.editUserInputOrientation.text()
        self.editUserInput.clear()
        self.editUserInputAlphanumericColor.clear()
        self.editUserInputShape.clear()
        self.editUserInputShapeColor.clear()
        self.editUserInputOrientation.clear()
        # TODO: instead of printing pass the reference for sending to interop
        print(self.getAlphanumeric)
        print(self.getAlphanumericColor)
        print(self.getShape)
        print(self.getShapeColor)
        print(self.getOrientation)
    
    def loadImage(self, viewer):
#        print(self.viewer.imgList)
        self.viewer.setPhoto(QPixmap(self.viewer.imgPath + self.viewer.imgList[self.viewer.imgNumber]))
        
    # Receive and display the signal when cropped pixmap is created
    @pyqtSlot(QPixmap)
    def showProcessedTarget(self, pixmap):
        self.processedTarget.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        self.processedTarget.setAlignment(Qt.AlignCenter)
        
    def about(self):
        QMessageBox.about(self, 
            "About KSU SUAS Image Analysis",
            """<b>KSU SUAS Image Analysis</b>
               <p>Copyright &copy; 2019 KSU SUAS, All Rights Reserved.
               <p>Python %s -- Qt %s -- PyQt %s on %s""" %(platform.python_version(),
                                                           QT_VERSION_STR, PYQT_VERSION_STR,
                                                           platform.system()) +
              """ <div>Icon made by <a href="https://www.flaticon.com/authors/smalllikeart"
              title="smalllikeart">smalllikeart</a> from <a href="https://www.flaticon.com/"
              title="Flaticon">www.flaticon.com</a></div>""")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet("QMainWindow { background: rgb(81,40,136) }")
    window.resize(800, 500)
    window.showMaximized()
    window.show()   
    window.start()
    app.exec_()
