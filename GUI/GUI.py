#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 12:49:01 2019

@author: Alex Kim
"""
###############################################################################
# OBC: Onboard computer (Odroid XU4)
# GCS: Ground Control Station (Image Analysis and Mission Planner PC)
###############################################################################
# __/\\\________/\\\_____/\\\\\\\\\\\____/\\\________/\\\_                           
#  _\/\\\_____/\\\//____/\\\/////////\\\_\/\\\_______\/\\\_                          
#   _\/\\\__/\\\//______\//\\\______\///__\/\\\_______\/\\\_                         
#    _\/\\\\\\//\\\_______\////\\\_________\/\\\_______\/\\\_                        
#     _\/\\\//_\//\\\_________\////\\\______\/\\\_______\/\\\_                       
#      _\/\\\____\//\\\___________\////\\\___\/\\\_______\/\\\_                      
#       _\/\\\_____\//\\\___/\\\______\//\\\__\//\\\______/\\\__                     
#        _\/\\\______\//\\\_\///\\\\\\\\\\\/____\///\\\\\\\\\/___                    
#         _\///________\///____\///////////________\/////////_____                   
# _____/\\\\\\\\\\\____/\\\________/\\\_____/\\\\\\\\\________/\\\\\\\\\\\___        
#  ___/\\\/////////\\\_\/\\\_______\/\\\___/\\\\\\\\\\\\\____/\\\/////////\\\_       
#   __\//\\\______\///__\/\\\_______\/\\\__/\\\/////////\\\__\//\\\______\///__      
#    ___\////\\\_________\/\\\_______\/\\\_\/\\\_______\/\\\___\////\\\_________     
#     ______\////\\\______\/\\\_______\/\\\_\/\\\\\\\\\\\\\\\______\////\\\______    
#      _________\////\\\___\/\\\_______\/\\\_\/\\\/////////\\\_________\////\\\___   
#       __/\\\______\//\\\__\//\\\______/\\\__\/\\\_______\/\\\__/\\\______\//\\\__  
#        _\///\\\\\\\\\\\/____\///\\\\\\\\\/___\/\\\_______\/\\\_\///\\\\\\\\\\\/___ 
#         ___\///////////________\/////////_____\///________\///____\///////////_____
# _____/\\\\\\\\\\\\__/\\\________/\\\__/\\\\\\\\\\\_        
#  ___/\\\//////////__\/\\\_______\/\\\_\/////\\\///__       
#   __/\\\_____________\/\\\_______\/\\\_____\/\\\_____      
#    _\/\\\____/\\\\\\\_\/\\\_______\/\\\_____\/\\\_____     
#     _\/\\\___\/////\\\_\/\\\_______\/\\\_____\/\\\_____    
#      _\/\\\_______\/\\\_\/\\\_______\/\\\_____\/\\\_____   
#       _\/\\\_______\/\\\_\//\\\______/\\\______\/\\\_____  
#        _\//\\\\\\\\\\\\/___\///\\\\\\\\\/____/\\\\\\\\\\\_ 
#         __\////////////_______\/////////_____\///////////__
###############################################################################
###############################################################################
###############################################################################
###############################################################################        
# Import modules
import sys, platform
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QLineEdit, 
                             QVBoxLayout, QAction, QSizePolicy, QHBoxLayout,
                             QGridLayout, QShortcut, QGraphicsView, QLabel,
                              QFrame, QToolButton, QMessageBox)
from PyQt5.QtCore import pyqtSlot, Qt, QThread, QTimer, QT_VERSION_STR, PYQT_VERSION_STR
from PyQt5.QtGui import QPixmap, QKeySequence, QIcon
from PhotoViewer import PhotoViewer
from ReadMissionPlannerData import ReadMPDataWorker
from DroneKit import DroneKitWorker
from CameraTriggerWorker import CamTrigWorker
# TODO: using EXIF orientation number rotate the target image
from PIL import Image, ExifTags
from numpy import sin, cos, arctan, pi, array#, tan, empty
    
class MainWindow(QMainWindow):
    '''
        Basic application workflow:
        GUI runs on the GCS computer.
        Camera control commands are sent from GCS to OBC over 5GHz
        Pictures will be taken at three second interval and save to shared directory
        between the air and ground.
    '''
    def __init__(self, parent=None):
        '''
            MainWindow Object to put together GUI layouts and its Widgets
        '''
#        super(MainWindow, self).__init__(parent)
        super().__init__()
        self.viewer = PhotoViewer(self)
        
        # For target localization
        self.pixelX = 0
        self.pixelY = 0
        
        self.flightNumber = 0
        
        # Add Window Title
        self.setWindowTitle('Team Spycat Image Analysis 1.0')
        
        # Add an Icon
        self.setWindowIcon(QIcon('icon/airport.svg'))
        
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
        toolButtonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # 'Connect Vehicle' button
        self.btnConnectVehicle = QToolButton(self)
        # self.btnConnectVehicle.setCheckable(True)
        self.btnConnectVehicle.setStyleSheet("QToolButton {background-color: red}")
        self.btnConnectVehicle.setSizePolicy(toolButtonSizePolicy)
        self.btnConnectVehicle.setText('Connect Vehicle')
        self.vehicleState = 0
        self.btnConnectVehicle.clicked.connect(self.btnConnectVehicleHandler)
        
        # 'Detect Camera' button
        self.btnDetectCam = QToolButton(self)
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
        
        self.btnPixInfo = QLabel(self)
        self.btnPixInfo.setText('<b>Pixel Info:</b>')
        self.btnPixInfo.setStyleSheet("QLabel { color: rgb(255,255,255)}") 

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
        self.cropImage.clicked.connect(self.pixInfo)
        
        # Display VFR HUD Items
        self.heading = QLabel('<b>Heading:</b>')
        self.heading.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.heading.setFixedWidth(100)
        self.headingValue = QLineEdit(self)
        self.headingValue.setReadOnly(True)
        self.headingValue.setFixedWidth(100)
        self.headingValue.setText('{}'.format(0))
        self.altitude = QLabel('<b>Altitude:</b>')
        self.altitude.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.altitude.setFixedWidth(100)
        self.altitudeValue = QLineEdit(self)
        self.altitudeValue.setReadOnly(True)
        self.altitudeValue.setFixedWidth(100)
        self.altitudeValue.setText('{}'.format(0))      
        self.latitude = QLabel('<b>Latitude:</b>')
        self.latitude.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.latitude.setFixedWidth(100)
        self.latitudeValue = QLineEdit(self)
        self.latitudeValue.setReadOnly(True)
        self.latitudeValue.setFixedWidth(100)
        self.latitudeValue.setText('{}'.format(0))
        self.longitude = QLabel('<b>Longitude:</b>')
        self.longitude.setStyleSheet("QLabel { color: rgb(255,255,255)}")                                
        self.longitude.setFixedWidth(100)
        self.longitudeValue = QLineEdit(self)
        self.longitudeValue.setReadOnly(True)
        self.longitudeValue.setFixedWidth(100)
        self.longitudeValue.setText('{}'.format(0))        
        
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
        VFR_HUD.addWidget(self.heading, 0, 0)
        VFR_HUD.addWidget(self.headingValue, 0, 1)        
        VFR_HUD.addWidget(self.altitude, 1, 0)
        VFR_HUD.addWidget(self.altitudeValue, 1, 1)
        VFR_HUD.addWidget(self.latitude, 2, 0)
        VFR_HUD.addWidget(self.latitudeValue, 2, 1)
        VFR_HUD.addWidget(self.longitude, 3, 0)
        VFR_HUD.addWidget(self.longitudeValue, 3, 1)
        VFR_HUD.addWidget(self.userInput, 4, 0)
        VFR_HUD.addWidget(self.editUserInput, 4, 1)
        VFR_HUD.addWidget(self.userInputAlphanumericColor, 5, 0)
        VFR_HUD.addWidget(self.editUserInputAlphanumericColor, 5, 1)        

        # Buttons layout
        Btnlayout = QVBoxLayout()
        Btnlayout.addWidget(self.btnConnectVehicle)
        Btnlayout.addWidget(self.btnDetectCam)
        Btnlayout.addWidget(self.btnCamTrig)
        Btnlayout.addWidget(self.btnLoad)
        Btnlayout.addLayout(ImgInfo)
        Btnlayout.addWidget(self.cropImage)
        Btnlayout.addLayout(VFR_HUD)
        Btnlayout.addStretch(1)
        ## Add the last processed target image
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
        self.timer.setInterval(1500) # update interval in ms (1.5 sec)
        self.timer.timeout.connect(self.updateImgDir)

        # Instantiate Worker Objects
        self.sendLinuxCmd = CamTrigWorker()
        self.sendLinuxCmd2 = CamTrigWorker()
        
        # Instantiate Thread Objects
        self.sendLinuxCmd_thread_startCamTrig = QThread()
        self.sendLinuxCmd_thread_detectCam = QThread()
        
        # Move Worker Objs to Thread
        self.sendLinuxCmd.moveToThread(self.sendLinuxCmd_thread_startCamTrig)
        self.sendLinuxCmd2.moveToThread(self.sendLinuxCmd_thread_detectCam)
        
        # Connect signals when threads start
        self.sendLinuxCmd_thread_startCamTrig.started.connect(self.sendLinuxCmd.sendMkdirCmd)
        self.sendLinuxCmd_thread_detectCam.started.connect(self.sendLinuxCmd2.sendDetCmd)
        
        # DroneKit vehicle connect thread
        self.connectToVehicle_thread = QThread()
        self.dronekit = DroneKitWorker()
        self.dronekit.moveToThread(self.connectToVehicle_thread)
        self.connectToVehicle_thread.started.connect(self.dronekit.connectVehicle)
        self.dronekit.finishedConnecting.connect(self.handleConnectedState)

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
    def closeVehicle(self):
        try:
            self.dronekit.vehicle.close()
            self.connectToVehicle_thread.quit
        except:
            self.connectToVehicle_thread.quit

    @pyqtSlot()
    def handleConnectedState(self):
        self.btnConnectVehicle.setText('Vehicle Connected')
        self.btnConnectVehicle.setStyleSheet("QToolButton {background-color: green}")   
        self.vehicleState = 2
    
    @pyqtSlot()
    def btnConnectVehicleHandler(self):
        if self.vehicleState == 0: # disconnected
            # if self.btnConnectVehicle.isChecked():
            self.btnConnectVehicle.setText('Vehicle Connecting...')
            self.btnConnectVehicle.setStyleSheet("QToolButton {background-color: yellow}")
            self.connectToVehicle_thread.start()
            self.vehicleState = 1
        elif self.vehicleState == 1: # connecting
            self.btnConnectVehicle.setText('Connect Vehicle')
            self.btnConnectVehicle.setStyleSheet("QToolButton {background-color: red}")
            self.closeVehicle()
            self.vehicleState = 0
        elif self.vehicleState == 2: # vehicle is connected. ask again
            quit_msg = "Are you sure you want to disconnect from the vehicle?"
            reply = QMessageBox.question(self, 'Message', 
                             quit_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.btnConnectVehicle.setText('Vehicle Disconnected')
                self.btnConnectVehicle.setStyleSheet("QToolButton {background-color: red}")    
                self.closeVehicle()
                self.vehicleState = 0
            elif reply == QMessageBox.No:
                self.vehicleState = 2

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', 
                         quit_msg, QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def btnCamTrigHandler(self):
        if self.btnCamTrig.isChecked():
            self.btnCamTrig.setText('Cancel Triggering Camera')
            self.sendLinuxCmd_thread_startCamTrig.start()
        else:
            self.btnCamTrig.setText('Start Triggering Camera')
            self.sendLinuxCmd.cancelTrigCmd()
            self.sendLinuxCmd.finishedTriggering.connect(self.sendLinuxCmd_thread_startCamTrig.quit)

    # TODO: wrap this method in QThread to display within GUI
    def pixInfo(self, pos): # TODO: methods to handle EXIF processing and calculations, read MP and GPS data
        self.reader = ReadMPDataWorker()
        # local variables
        altitude, heading, latitude, longitude = self.reader.readFromGPSData(self.viewer.imgNumber)        
        orientation, angleOfViewX, angleOfViewY, imgW, imgH = self.getEXIF()

        distReal = array([(2*altitude)/cos(angleOfViewX/2), (2*altitude)/cos(angleOfViewY/2)])
        scale = array([distReal[0]/imgW, distReal[1]/imgH])
        offsetTarget = array([scale[0]*self.pixelX, scale[1]*self.pixelY])
        # TODO: attach the camera aligned with the Pixhawk's direction for consistent heading
        mapRealtoCamera = array([cos(heading), -sin(heading)], [sin(heading), cos(heading)])
        
        posReal = mapRealtoCamera.dot(offsetTarget)
        targetGPS = array([posReal[0]/longitude, posReal[1]/latitude])
        
        # display the target's info on GUI
        self.headingValue.setText('{}'.format(heading))
        self.altitudeValue.setText('{}'.format(altitude))
        self.latitudeValue.setText('{}'.format(targetGPS[1]))
        self.longitudeValue.setText('{}'.format(targetGPS[0]))
    
    def keyPress(self, imgNumber):
        self.loadedImgNumber.setText('{}'.format(imgNumber))

    def photoClick(self, pos):
        self.viewer.toggleDragMode()
        if self.viewer.dragMode()  == QGraphicsView.NoDrag:
            self.editPixInfo.setText('{0:.0f}, {1:.0f}'.format(pos.x(),pos.y()))
            self.pixelX = pos.x()
            self.pixelY = pos.y()
            self.viewer.toggleDragMode()
            
    def imageCrop(self, pos):
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
    
    def loadImage(self):
        self.viewer.setPhoto(QPixmap(self.viewer.imgPath + self.viewer.imgList[self.viewer.imgNumber]))
        
    def getEXIF(self):
        image = Image.open(self.viewer.imgPath + self.viewer.imgList[self.viewer.imgNumber])
        exifData = image._getexif()
        orientation = 0
    #    dateTime    = 0.0
        imgWidth    = 0
        imgHeight   = 0
        focalLen    = 0.0    # focal length in mm
        angleOfViewX = 0.0 # AOV along the width of the sensor (Sony A6000)
        angleOfViewY = 0.0 # AOV along the height of the sensor (Sony A6000)
        for tag, value in exifData.items():
            if ExifTags.TAGS.get(tag)  == 'Orientation':
                orientation = value
            elif ExifTags.TAGS.get(tag) == 'SubsecTimeDigitized':
    #            print(value)
                pass
            elif ExifTags.TAGS.get(tag) == 'DateTime':
                pass
    #            print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'FocalLength':
                focalLen = value[0]/value[1]
                angleOfViewX = 2*arctan(23.5/(2*focalLen))*(180/pi)
                angleOfViewY = 2*arctan(15.6/(2*focalLen))*(180/pi)
            elif ExifTags.TAGS.get(tag) == 'ExifImageWidth':
                imgWidth = value
            elif ExifTags.TAGS.get(tag) == 'ExifImageHeight':
                imgHeight = value
            elif ExifTags.TAGS.get(tag) == 'ExposureTime':
                pass
            elif ExifTags.TAGS.get(tag) == 'ISOSpeedRatings':
                pass
            
        return orientation, angleOfViewX, angleOfViewY, imgWidth, imgHeight        
    
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