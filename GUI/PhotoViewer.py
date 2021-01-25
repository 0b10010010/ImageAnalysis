#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 01:03:24 2019

@author: Alex Kim
"""

from os import listdir, path, system
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QFrame, QRubberBand)
from PyQt5.QtCore import pyqtSignal, QPointF, Qt, QRectF, QPoint, QRect, QSize
from PyQt5.QtGui import QBrush, QColor, QPixmap

###############################################################################
###############################################################################
###############################################################################
class PhotoViewer(QGraphicsView):
    '''
        Handles image display related methods such as scrolling zoom, drag to
        crop and etc.
    '''
    # pyqtSignals for respective slots
    photoClicked = pyqtSignal(QPointF)
    keyPressed   = pyqtSignal(int)
    rectChanged  = pyqtSignal(QRect)
    imgReady     = pyqtSignal(QPixmap)
    
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
        self.setBackgroundBrush(QBrush(QColor(209,209,209)))
        self.setFrameShape(QFrame.NoFrame)
#        self.imgPath = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/img/'
        self.imgPath = '/home/spykat/Desktop/imgTargetDir/' # TODO: This is the shared dir between onboard computer and GCS
        # self.imgPath = '/home/spykat/Desktop/TestFlightDataBackUp/imgTargetDirBackUp/imgTargetDir/'
#        self.imgPath = '/home/alexk/Desktop/Capture#1/'
        self.imgList = listdir(self.imgPath)
        self.imgList.sort()
        self.listLim = len(self.imgList)
        self.imgNumber = 0
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.changeRubberBand = False
        
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
            elif event.button() == Qt.RightButton:
                self.changeRubberBand = True
                self.origin = event.pos()
                self.rubberBand.setGeometry(QRect(self.origin, QSize()))
                self.rectChanged.emit(self.rubberBand.geometry())
                self.rubberBand.show()
                self.currentQRectTopLeft  = self.mapToScene(self.origin).toPoint()
            QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.hasPhoto():
            if self.changeRubberBand == True:
                self.moveBand = event.pos()
                self.rubberBand.setGeometry(QRect(self.origin, self.moveBand).normalized())
                self.rectChanged.emit(self.rubberBand.geometry())
            QGraphicsView.mouseMoveEvent(self, event)
        
    def mouseReleaseEvent(self, event):
        if self.hasPhoto():
            if self.changeRubberBand == True:
                self.changeRubberBand = False
                self.bottomRight = event.pos()
                self.currentQRectBotRight = self.mapToScene(self.bottomRight).toPoint()
            QGraphicsView.mouseReleaseEvent(self, event)
    
    def saveCropEvent(self):
        self.rubberBand.hide()
        self.imgCrop = (self.currentQRectTopLeft.x(), self.currentQRectTopLeft.y(),
                        self.currentQRectBotRight.x(), self.currentQRectBotRight.y())
        topLeftX   = min(self.currentQRectTopLeft.x(), self.currentQRectBotRight.x())
        topLeftY   = min(self.currentQRectTopLeft.y(), self.currentQRectBotRight.y())
        cropWidth  = abs(self.currentQRectTopLeft.x() - self.currentQRectBotRight.x())
        cropHeight = abs(self.currentQRectTopLeft.y() - self.currentQRectBotRight.y())
        self.cropQPixmap = self._photo.pixmap().copy(topLeftX, topLeftY, cropWidth, cropHeight)
        
        self.cropQPixmap.save('ProcessedTargets/Obj{}.png'.format(self.imgNumber))
#        self.cropQPixmap.save('Obj%d.jpg' %self.imgNumber)
        self.imgReady.emit(self.cropQPixmap) # emit signal that cropped img is ready

        
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
        nextImg = QPixmap(self.imgPath + self.imgList[self.imgNumber])
        self.setPhoto(nextImg)

    def updateImgDirectory(self):
        self.imgList = listdir(self.imgPath)
        self.listLim = len(self.imgList)
        self.imgList.sort()
