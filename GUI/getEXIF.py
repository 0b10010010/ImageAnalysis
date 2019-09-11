#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 20:32:48 2019

@author: alexk
"""

from PIL import Image, ExifTags
from numpy import sin, cos, tan, arctan, pi, array, empty

def getExif(imgPath, imgList, imgNumber, pixelX, pixelY): # TODO: Create a dictionary instead of printing
    image = Image.open(imgPath + imgList[imgNumber])
    exifData = image._getexif()
    orientation = 0
#    dateTime    = 0.0
    imgWidth    = 0
    imgHeight   = 0
    focalLen    = 0    # focal length in mm
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
    print(orientation)
#    print(dateTime)
    print(pixelX)
    print(pixelY)
    print(focalLen)
    print(angleOfViewX, angleOfViewY)
    print(imgWidth, imgHeight)