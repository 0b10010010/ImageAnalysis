#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 12:49:01 2019

@author: alexk
"""

import sys
import platform
from os import listdir, path
from PIL import Image, ExifTags
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QLineEdit, 
                             QVBoxLayout, QAction, QMessageBox, QFileDialog,
                             QSizePolicy, QPushButton, QHBoxLayout, QLabel,
                             QGridLayout, QShortcut, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFrame,
                             QToolButton, QRubberBand)
from PyQt5.QtCore import (pyqtSignal, QPointF, Qt, QRectF, QRect, QSize, QPoint,
                          QT_VERSION_STR, PYQT_VERSION_STR)
from PyQt5.QtGui import QBrush, QColor, QPixmap, QKeySequence, QKeyEvent

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
        self.path = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/img/' # TODO: set to correct path
#        self.path = '/home/spycat/Desktop/ImageAnalysis/GUI/Img/'
        self.imgList = listdir(self.path)
        self.listLim = len(self.imgList)
        self.imgNumber = 0
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.changeRubberBand = False
        
    def getExif(self): # TODO: Create a dictionary instead of printing
        img = Image.open(self.path + self.imgList[self.imgNumber])
        exifData = img._getexif()
        for tag, value in exifData.items():
            if ExifTags.TAGS.get(tag) == 'Orientation':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'DateTime':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'FocalLength':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'ExifImageWidth':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'ExifImageHeight':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'ExposureTime':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
            elif ExifTags.TAGS.get(tag) == 'ISOSpeedRatings':
                print('%s = %s' % (ExifTags.TAGS.get(tag), value))
    
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

#    def toggleCropMode(self):
#        if self.dragMode() == QGraphicsView.ScrollHandDrag:
#            self.setDragMode(QGraphicsView.NoDrag)
#            self.changeRubberBand == True
#        elif not self._photo.pixmap().isNull():
#            self.setDragMode(QGraphicsView.ScrollHandDrag)     

    def mousePressEvent(self, event):
#        if self._photo.isUnderMouse():
        if event.button() == Qt.LeftButton:
            self.photoClicked.emit(self.mapToScene(event.pos()))
            super(PhotoViewer, self).mousePressEvent(event) 
        elif event.button() == Qt.RightButton:
            self.changeRubberBand = True
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rectChanged.emit(self.rubberBand.geometry())
            self.rubberBand.show()   
#        super(PhotoViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.changeRubberBand == True:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
            self.rectChanged.emit(self.rubberBand.geometry())
        QGraphicsView.mouseMoveEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        if self.changeRubberBand == True:
            self.changeRubberBand = False
            self.cropEvent()
        QGraphicsView.mouseReleaseEvent(self, event)
    
    def cropEvent(self):
#        self.rubberBand.hide()
        self.currentQRect = self.rubberBand.geometry()
#        self.rubberBand.deleteLater()
    
    def saveCropEvent(self):
        self.rubberBand.hide()
#        self.rubberBand.deleteLater()
        self.cropQPixmap = self._photo.pixmap().copy(self.currentQRect)
        self.cropQPixmap.save('cropped.png')
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right or key == Qt.Key_Down:
            self.imgNumber += 1
            if self.listLim <= self.imgNumber:
                self.imgNumber = self.listLim - 1
            self.nextImage(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        elif key == Qt.Key_Left or key == Qt.Key_Up:
            self.imgNumber -= 1
            if self.imgNumber <= 0:
                self.imgNumber = 0
            self.nextImage(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        else:
            super(PhotoViewer, self).keyPressEvent(event)

    def nextImage(self, imgNumber):
        pixmap = QPixmap(self.path + self.imgList[self.imgNumber])
        self.setPhoto(pixmap)


class ReadTelemetryLog():
    def __init__(self):
        self.dict = {}
        self.infoByFrame = []
        self.lattitudes = []
        self.longitudes = []
        self.logFilePath = '/home/spycat/Desktop/SUASImageAnalysis/GUI/CamFeedbackTest/flight.txt'
        
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


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.viewer = PhotoViewer(self)
        self.viewer.nextImage(self.viewer.imgNumber)
        self.readLog = ReadTelemetryLog()
        
        # Add Window Title
        self.setWindowTitle('Team Spycat Image Analysis 0.0')
        
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
#        self.actionAbout.triggered.connect(self.about)
        self.menuHelp.addActions([self.actionAbout])

        #######################################################################
        # CREATE CENTRAL WIDGET
        #######################################################################
        
        self.widget = QDialog()

        #######################################################################
        # LAYOUTS
        #######################################################################

        # 'Load image' button
        self.btnLoad = QToolButton(self)
        toolButtonSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.btnLoad.setSizePolicy(toolButtonSizePolicy)
        self.btnLoad.setText('Load Image')
        self.btnLoad.clicked.connect(self.viewer.nextImage)
        
        self.loadedImg = QLabel('Frame #:')
        self.loadedImg.setFixedWidth(100)
        self.loadedImgNumber = QLineEdit(self)
        self.loadedImgNumber.setReadOnly(True)
        self.loadedImgNumber.setFixedWidth(100)
        self.loadedImgNumber.setText('%d' %self.viewer.imgNumber)
        self.viewer.keyPressed.connect(self.keyPress)

        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QToolButton(self)
        self.btnPixInfo.setText('Pixel Info. Mode')
        self.btnPixInfo.setCheckable(True)
        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.editPixInfo.setFixedWidth(100)
        self.viewer.photoClicked.connect(self.photoClick)
        
        # For image processing
        self.cropImage = QToolButton()
        self.cropImage.setText('Crop')
        self.cropImage.clicked.connect(self.imageCrop)
#        self.cropImage.setCheckable(True)
#        self.cropImage.clicked.connect(self.crop)
#        self.viewer.rectChanged.connect(self.imageCrop)
        
        # For image processing
        self.processImage = QToolButton(self)
        self.processImage.setSizePolicy(toolButtonSizePolicy)
        self.processImage.setText('Process')
        self.processImage.clicked.connect(ReadTelemetryLog.transform)

        # Image layout
        Imglayout = QHBoxLayout(self)
        Imglayout.addWidget(self.viewer)

        # Image Information
        ImgInfo = QGridLayout(self)
        ImgInfo.addWidget(self.loadedImg, 0, 0)
        ImgInfo.addWidget(self.loadedImgNumber, 0, 1)
        ImgInfo.addWidget(self.btnPixInfo, 1, 0)
        ImgInfo.addWidget(self.editPixInfo, 1, 1)
    
        # Buttons layout
        Btnlayout = QVBoxLayout(self)
        Btnlayout.addWidget(self.btnLoad)
        Btnlayout.addLayout(ImgInfo)
        Btnlayout.addWidget(self.cropImage)
        Btnlayout.addWidget(self.processImage)
        Btnlayout.addStretch(1)
        
        # Final GUI layout
        GUILayout = QHBoxLayout()
        GUILayout.addLayout(Imglayout)
        GUILayout.addLayout(Btnlayout)
        
        self.widget.setLayout(GUILayout)
        self.setCentralWidget(self.widget)

    def pixInfo(self):
        self.viewer.toggleDragMode()
        print(self.viewer.getExif())
        print('Frame #: %d' % self.viewer.imgNumber)
        self.readLog.readAttitude()   
        
    def keyPress(self, imgNumber):
        self.loadedImgNumber.setText('%d' % imgNumber)

    def photoClick(self, pos):
        if self.viewer.dragMode()  == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
            
    def imageCrop(self):
        self.viewer.saveCropEvent()
        
    
    
#    def about(self):
#        QMessageBox.about(self, 
#            "About Function Evaluator",
#            """<b>Function Evaluator</b>
#               <p>Copyright &copy; 2016 Jeremy Roberts, All Rights Reserved.
#               <p>Python %s -- Qt %s -- PyQt %s on %s""" %
#            (platform.python_version(),
#             QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    window.show()
    exit(app.exec_())