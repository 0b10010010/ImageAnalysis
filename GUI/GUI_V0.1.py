#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 12:49:01 2019

@author: Alex Kim
"""

import sys, platform, getEXIF, camTrigWorker
from os import listdir, path
from PIL import Image, ExifTags
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QLineEdit, 
                             QVBoxLayout, QAction, QSizePolicy, QHBoxLayout,
                             QGridLayout, QShortcut, QGraphicsView, QLabel,
                             QGraphicsScene, QGraphicsPixmapItem, QFrame,
                             QToolButton, QRubberBand, QMessageBox)
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QPointF, Qt, QRectF, QThread, QObject,
                          QRect, QSize, QTimer, QT_VERSION_STR, PYQT_VERSION_STR)
from PyQt5.QtGui import QBrush, QColor, QPixmap, QKeySequence, QIcon

###############################################################################
###############################################################################
###############################################################################
class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPointF)
    keyPressed   = pyqtSignal(int)
    rectChanged  = pyqtSignal(QRect)
    
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.imgPath = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/img/' # TODO: set to correct path
#        self.path = '/home/spycat/Desktop/ImageAnalysis/GUI/Img/'
        self.imgList = listdir(self.imgPath)
        self.imgList.sort()
        self.listLim = len(self.imgList)
        self.imgNumber = 0
#        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.changeRubberBand = False
        
        self.obj = camTrigWorker.camTrigWorker()
        self.obj_thread = QThread()
        
        self.obj.respReady.connect(self.onRespReady)
        self.obj.moveToThread(self.obj_thread)
        self.obj.finished.connect(self.obj_thread.quit)
#        self.thread.started.connect(self.obj.sendTrigCmd)
        self.obj_thread.start()

    def onRespReady(self, result):
        pass
        
#    def getExif(self): # TODO: Create a dictionary instead of printing
#        img = Image.open(self.imgPath + self.imgList[self.imgNumber])
#        exifData = img._getexif()
#        for tag, value in exifData.items():
#            if ExifTags.TAGS.get(tag) == 'Orientation':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'DateTime':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'FocalLength':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'ExifImageWidth':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'ExifImageHeight':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'ExposureTime':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
#            elif ExifTags.TAGS.get(tag) == 'ISOSpeedRatings':
#                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
    
    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)  

    def mousePressEvent(self, event):
        if self.hasPhoto():
            if event.button() == Qt.LeftButton:
                self.photoClicked.emit(self.mapToScene(event.pos()))
    #            super(PhotoViewer, self).mousePressEvent(event) 
            elif event.button() == Qt.RightButton:
                self.changeRubberBand = True
                self.origin = event.pos()
                self.rubberBand.setGeometry(QRect(self.origin, QSize()))
                self.rectChanged.emit(self.rubberBand.geometry())
                self.rubberBand.show()
                self.currentQRectTopLeft  = self.mapToScene(self.origin).toPoint()
            QGraphicsView.mousePressEvent(self, event)
#        super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.hasPhoto():
            if self.changeRubberBand == True:
                self.moveBand = event.pos()
                self.rubberBand.setGeometry(QRect(self.origin, self.moveBand).normalized())
                self.rectChanged.emit(self.rubberBand.geometry())
            QGraphicsView.mouseMoveEvent(self, event)
#        super(PhotoViewer, self).mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if self.hasPhoto():
            if self.changeRubberBand == True:
                self.changeRubberBand = False
                self.bottomRight = event.pos()
                self.currentQRectBotRight = self.mapToScene(self.bottomRight).toPoint()
            QGraphicsView.mouseReleaseEvent(self, event)
#        super(PhotoViewer, self).mouseReleaseEvent(event)
    
    def saveCropEvent(self):
        self.rubberBand.hide()
        self.imgCrop = (self.currentQRectTopLeft.x(), self.currentQRectTopLeft.y(),
                        self.currentQRectBotRight.x(), self.currentQRectBotRight.y())
        topLeftX   = min(self.currentQRectTopLeft.x(), self.currentQRectBotRight.x())
        topLeftY   = min(self.currentQRectTopLeft.y(), self.currentQRectBotRight.y())
        cropWidth  = abs(self.currentQRectTopLeft.x() - self.currentQRectBotRight.x())
        cropHeight = abs(self.currentQRectTopLeft.y() - self.currentQRectBotRight.y())
        
        self.cropQPixmap = self._photo.pixmap().copy(topLeftX, topLeftY, cropWidth, cropHeight)                                            
        self.cropQPixmap.save('Obj%d.png' %self.imgNumber)
        # TODO: save the target images to ProcessedTargets directory
#        self.rubberBand.deleteLater()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right or key == Qt.Key_Down:
#            self.updateImgDirectory()
            self.imgNumber += 1
            if self.listLim <= self.imgNumber:
                self.imgNumber = self.listLim - 1
            self.nextImage(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        elif key == Qt.Key_Left or key == Qt.Key_Up:
#            self.updateImgDirectory()
            self.imgNumber -= 1
            if self.imgNumber <= 0:
                self.imgNumber = 0
            self.nextImage(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        else:
            super(PhotoViewer, self).keyPressEvent(event)

    def nextImage(self, imgNumber):
        nextImg = QPixmap(self.imgPath + self.imgList[self.imgNumber])
        self.setPhoto(nextImg)

    def updateImgDirectory(self):
        self.imgList = listdir(self.imgPath)
        self.listLim = len(self.imgList)
        self.imgList.sort()
        
    def trigLinCmd(self):
        exe = executeLinuxCommand
        exe.triggerCam()
        
###############################################################################
###############################################################################
###############################################################################
class ReadTelemetryLog():
    def __init__(self):
        self.dict = {}
        self.infoByFrame = []
        self.lattitudes = []
        self.longitudes = []
        self.logFilePath = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/flight.txt'
        
    def readAttitude(self):
        with open(self.logFilePath, 'rt') as in_file:
            for line in in_file:
#                self.infoByFrame.append(line.split(','))
                self.infoByFrame.append(line[39::])
#                self.longitudes.append(line.)
#        print(self.infoByFrame)
        for lines in self.infoByFrame:
            self.lattitudes.append(lines[76:86].split(',')[0])
        print(self.lattitudes[0])
        
    def transform():
        pass

###############################################################################
###############################################################################
###############################################################################
#class executeLinuxCommand():
#    # read https://gist.github.com/bortzmeyer/1284249
#    def __init__(self):
#        self.host = "odroid@odroid"        
#        # gphoto2 shell commands
#        self.detectCam = 'gphoto2 --auto-detect'
#        self.triggerCam = 'gphoto2 --capture-image-and-download --interval 3'
#        self.result = []
#
#    def detectCamera(self):
##        self.cmdDetectCam = subprocess.Popen(self.detectCam, stdout=subprocess.PIPE, shell=True)
#        self.cmdDetectCam = subprocess.Popen(["ssh", "%s" % self.host, self.detectCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        self.result = self.cmdDetectCam.stdout.readlines()
#        if self.result == []:
#            error = self.cmdDetectCam.stderr.readlines()
#            print(sys.stderr, "ERROR: %s" % error)
#        else:
#            print(self.result)
#            
#    def triggerCamera(self):
##        self.cmdTrigCam = subprocess.Popen(self.triggerCam, stdout=subprocess.PIPE, shell=True)
#        self.cmdTrigCam = subprocess.Popen(["ssh", "%s" % self.host, self.triggerCam], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        self.result = self.cmdTrigCam.stdout.readlines()
#        if self.result == []:
#            error = self.cmdTrigCam.stderr.readlines()
#            print(sys.stderr, "ERROR: %s" % error)
#        else:
#            print(self.result)
        
###############################################################################
###############################################################################
###############################################################################            
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.viewer = PhotoViewer(self)
        self.readLog = ReadTelemetryLog()
        
        # Add Window Title
        self.setWindowTitle('Team Spycat Image Analysis 0.0')
        
        # Add an Icon
        self.setWindowIcon(QIcon('airport.svg')) # <div>Icons made by <a href="https://www.flaticon.com/authors/smalllikeart" title="smalllikeart">smalllikeart</a> from <a href="https://www.flaticon.com/"         title="Flaticon">www.flaticon.com</a></div>
        
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
#        self.actionSaveAs = QAction("&Save As", self)
#        self.actionSaveAs.triggered.connect(self.saveas)
        self.actionQuit = QAction("&Quit", self)
        self.actionQuit.triggered.connect(self.close)
#        self.menuFile.addActions([self.actionSaveAs, self.actionQuit])
        self.menuFile.addActions([self.actionQuit])
        
        # Create the Help menu
        self.menuHelp = self.menuBar().addMenu("&Help")
        self.actionAbout = QAction("&About",self)
        self.actionAbout.triggered.connect(self.about)
        self.menuHelp.addActions([self.actionAbout])

        #######################################################################
        # CREATE CENTRAL WIDGET
        #######################################################################
        
        self.widget = QDialog()

        #######################################################################
        # LAYOUTS
        #######################################################################
        
        # 'Start Triggering Camera' button
        self.btnDetectCam = QToolButton(self)
        toolButtonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btnDetectCam.setSizePolicy(toolButtonSizePolicy)
        self.btnDetectCam.setText('Detect Camera')
        self.btnDetectCam.clicked.connect(self.viewer.obj.sendDetCmd)

        # 'Start Triggering Camera' button
        self.btnCamTrig = QToolButton(self)
        self.btnCamTrig.setCheckable(True)
        self.btnCamTrig.setStyleSheet("QToolButton {background-color: red}"
                                      "QToolButton:checked {background-color: green}")
        self.btnCamTrig.setSizePolicy(toolButtonSizePolicy)
        self.btnCamTrig.setText('Start Triggering Camera')
        self.btnCamTrig.clicked.connect(self.viewer.obj.sendTrigCmd)

        # TODO: when trigger button gets pressed create folder and put images there
        
        # TODO: add more buttons to abort camera trigger or other linux cmds
        
        # 'Load image' button
        self.btnLoad = QToolButton(self)
        self.btnLoad.setSizePolicy(toolButtonSizePolicy)
        self.btnLoad.setText('Load Image')
        self.btnLoad.clicked.connect(self.loadImage)
        
        self.loadedImg = QLabel('Frame #:')
        self.loadedImg.setFixedWidth(100)
        self.loadedImgNumber = QLineEdit(self)
        self.loadedImgNumber.setReadOnly(True)
        self.loadedImgNumber.setFixedWidth(100)
        self.loadedImgNumber.setText('%d' %self.viewer.imgNumber)
        self.viewer.keyPressed.connect(self.keyPress)

        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QLabel(self)
        self.btnPixInfo.setText('Pixel Info')
#        self.btnPixInfo.setCheckable(True)
#        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.editPixInfo.setFixedWidth(100)
        self.viewer.photoClicked.connect(self.photoClick)
        
        # For image processing
        self.cropImage = QToolButton(self)
        self.cropImage.setSizePolicy(toolButtonSizePolicy)
        self.cropImage.setText('Crop and Process')
        self.cropImage.clicked.connect(self.imageCrop)
#        self.cropImage.clicked.connect(self.readLog.transform)
        
        # Image layout
        Imglayout = QHBoxLayout()
        Imglayout.addWidget(self.viewer)

        # Image Information
        ImgInfo = QGridLayout()
        ImgInfo.addWidget(self.loadedImg, 0, 0)
        ImgInfo.addWidget(self.loadedImgNumber, 0, 1)
        ImgInfo.addWidget(self.btnPixInfo, 1, 0)
        ImgInfo.addWidget(self.editPixInfo, 1, 1)
        
        # Buttons layout
        Btnlayout = QVBoxLayout()
        Btnlayout.addWidget(self.btnDetectCam)
        Btnlayout.addWidget(self.btnCamTrig)
        Btnlayout.addWidget(self.btnLoad)
        Btnlayout.addLayout(ImgInfo)
        Btnlayout.addWidget(self.cropImage)
        Btnlayout.addStretch(1)
        
        # Final GUI layout
        GUILayout = QHBoxLayout()
        GUILayout.addLayout(Imglayout)
        GUILayout.addLayout(Btnlayout)
        
        self.widget.setLayout(GUILayout)
        self.setCentralWidget(self.widget)
        
        # QTimer for updating image directory with new images taken
        self.timer = QTimer(self)
        self.timer.setInterval(3000) # update interval in ms (3 sec)
        self.timer.timeout.connect(self.updateImgDir)
    
    def start(self):
        # start QTimer thread
        self.timer.start()
        # use stop() to stop
#        self.timer.stop()
    
    @pyqtSlot()
    def updateImgDir(self):
        self.viewer.updateImgDirectory()

    @pyqtSlot(str)
    def printStatus(self, status):
        print(self.viewer.obj.respReady)
#    def pixInfo(self):
#        self.viewer.toggleDragMode()
#        print(self.viewer.getExif())
#        print('Frame #: %d' % self.viewer.imgNumber)
#        self.readLog.readAttitude()
        
    def keyPress(self, imgNumber):
        self.loadedImgNumber.setText('%d' % imgNumber)

    def photoClick(self, pos):
        self.viewer.toggleDragMode()
        if self.viewer.dragMode()  == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
            self.viewer.toggleDragMode()
            
    def imageCrop(self):
        getPixel = self.editPixInfo.text().split(',') # pixel location of clicked target
        getEXIF.getExif(self.viewer.imgPath, self.viewer.imgList, self.viewer.imgNumber, getPixel[0], getPixel[1])
        self.viewer.saveCropEvent()
    
    def loadImage(self):
        self.viewer.setPhoto(QPixmap(self.viewer.imgPath + self.viewer.imgList[self.viewer.imgNumber]))
        
    def triggerCam(self):
        pass
        
    def about(self):
        QMessageBox.about(self, 
            "About KSU SUAS Image Analysis",
            """<b>KSU SUAS Image Analysis</b>
               <p>Copyright &copy; 2019 KSU SUAS, All Rights Reserved.
               <p>Python %s -- Qt %s -- PyQt %s on %s""" %
            (platform.python_version(),
             QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 500)
    window.showMaximized()
    window.show()   
    window.start()
    app.exec_()
