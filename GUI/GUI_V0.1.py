#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 12:49:01 2019

@author: Alex Kim, Braedon Smith
"""

import sys
from os import listdir, path
from PIL import Image, ExifTags
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialog, QLineEdit, 
                             QVBoxLayout, QAction, QSizePolicy, QHBoxLayout,
                             QLabel, QGridLayout, QShortcut, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFrame,
                             QToolButton, QRubberBand)
from PyQt5.QtCore import (pyqtSignal, QPointF, Qt, QRectF, QRect, QSize, QPoint)
from PyQt5.QtGui import QBrush, QColor, QPixmap, QKeySequence, QKeyEvent


class PhotoViewer(QGraphicsView):
    photoClicked = pyqtSignal(QPointF)
    keyPressed = pyqtSignal(int)
    rectChanged = pyqtSignal(QRect)
    
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
        self.path = path.dirname(path.realpath(__file__)) + '/CamFeedbackTest/img/'  # TODO: set to correct path
#        self.path = '/home/spycat/Desktop/ImageAnalysis/GUI/Img/'
        self.imgList = listdir(self.path)
        self.listLim = len(self.imgList)
        self.imgNumber = 0
        self.origin = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.changeRubberBand = False
        
    def get_exif(self):
        img = Image.open(self.path + self.imgList[self.imgNumber])

        return {
            ExifTags.TAGS[k]: v
            for k, v in img._getexif().items()
            if k in ExifTags.TAGS
        }
    
    def has_photo(self):
        """
        :return: Whether an image has been loaded
        """
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())

        if not rect.isNull():
            self.setSceneRect(rect)

            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                view_rect = self.viewport().rect()
                scene_rect = self.transform().mapRect(rect)
                factor = min(view_rect.width() / scene_rect.width(),
                             view_rect.height() / scene_rect.height())
                self.scale(factor, factor)

            self._zoom = 0

    def set_photo(self, pixmap=None):
        """
        Sets the photo currently in view.
        :param pixmap: The photo to be displayed
        """
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
        if self.has_photo():
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

    def toggle_drag_mode(self):
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
            self.crop_event()

        QGraphicsView.mouseReleaseEvent(self, event)
    
    def crop_event(self):
#        self.rubberBand.hide()
        self.currentQRect = self.rubberBand.geometry()
#        self.rubberBand.deleteLater()
    
    def save_crop_event(self):
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
            self.next_image(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        elif key == Qt.Key_Left or key == Qt.Key_Up:
            self.imgNumber -= 1
            if self.imgNumber <= 0:
                self.imgNumber = 0
            self.next_image(self.imgNumber)
            self.keyPressed.emit(self.imgNumber)
        else:
            super(PhotoViewer, self).keyPressEvent(event)

    def next_image(self, img_number):
        pixmap = QPixmap(self.path + self.imgList[self.imgNumber])
        self.set_photo(pixmap)


class ReadTelemetryLog:
    def __init__(self):
        self.dict = {}
        self.infoByFrame = []
        self.latitudes = []
        self.longitudes = []
        self.logFilePath = '/home/spycat/Desktop/SUASImageAnalysis/GUI/CamFeedbackTest/flight.txt'
        
    def read_attitude(self):
        with open(self.logFilePath, 'rt') as in_file:
            for line in in_file:
#                self.infoByFrame.append(line.split(','))
                self.infoByFrame.append(line[39::])
#                self.longitudes.append(line.)
#        print(self.infoByFrame)

        for lines in self.infoByFrame:
            self.latitudes.append(lines[76:86].split(',')[0])
        print(self.latitudes[0])
        
    def transform(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.viewer = PhotoViewer(self)
        self.viewer.next_image(self.viewer.imgNumber)
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
        tool_button_size_policy = QSizePolicy(QSizePolicy.Preferred,
                                              QSizePolicy.Fixed)
        self.btnLoad.setSizePolicy(tool_button_size_policy)
        self.btnLoad.setText('Load Image')
        self.btnLoad.clicked.connect(self.viewer.next_image)
        
        self.loadedImg = QLabel('Frame #:')
        self.loadedImg.setFixedWidth(100)
        self.loadedImgNumber = QLineEdit(self)
        self.loadedImgNumber.setReadOnly(True)
        self.loadedImgNumber.setFixedWidth(100)
        self.loadedImgNumber.setText('%d' % self.viewer.imgNumber)
        self.viewer.keyPressed.connect(self.key_press)

        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo = QToolButton(self)
        self.btnPixInfo.setText('Pixel Info. Mode')
        self.btnPixInfo.setCheckable(True)
        self.btnPixInfo.clicked.connect(self.pix_info)
        self.editPixInfo = QLineEdit(self)
        self.editPixInfo.setReadOnly(True)
        self.editPixInfo.setFixedWidth(100)
        self.viewer.photoClicked.connect(self.photo_click)
        
        # For image processing
        self.cropImage = QToolButton()
        self.cropImage.setText('Crop')
        self.cropImage.clicked.connect(self.image_crop)
#        self.cropImage.setCheckable(True)
#        self.cropImage.clicked.connect(self.crop)
#        self.viewer.rectChanged.connect(self.imageCrop)
        
        # For image processing
        self.processImage = QToolButton(self)
        self.processImage.setSizePolicy(tool_button_size_policy)
        self.processImage.setText('Process')
        self.processImage.clicked.connect(ReadTelemetryLog.transform)

        # Image layout
        img_layout = QHBoxLayout(self)
        img_layout.addWidget(self.viewer)

        # Image Information
        img_info = QGridLayout(self)
        img_info.addWidget(self.loadedImg)
        img_info.addWidget(self.loadedImgNumber)
        img_info.addWidget(self.btnPixInfo)
        img_info.addWidget(self.editPixInfo)
    
        # Buttons layout
        button_layout = QVBoxLayout(self)
        button_layout.addWidget(self.btnLoad)
        button_layout.addLayout(img_info)
        button_layout.addWidget(self.cropImage)
        button_layout.addWidget(self.processImage)
        button_layout.addStretch(1)
        
        # Final GUI layout
        gui_layout = QHBoxLayout()
        gui_layout.addLayout(img_layout)
        gui_layout.addLayout(button_layout)
        
        self.widget.setLayout(gui_layout)
        self.setCentralWidget(self.widget)

    def pix_info(self):
        self.viewer.toggle_drag_mode()
        print(self.viewer.get_exif())
        print('Frame #: %d' % self.viewer.imgNumber)
        self.readLog.read_attitude()
        
    def key_press(self, img_number):
        self.loadedImgNumber.setText('%d' % img_number)

    def photo_click(self, pos):
        if self.viewer.dragMode() == QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
            
    def image_crop(self):
        self.viewer.save_crop_event()
        

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
