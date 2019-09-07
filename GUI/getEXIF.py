#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 20:32:48 2019

@author: alexk
"""

from PIL import Image, ExifTags

def getExif(imgPath, imgList, imgNumber, pixelX, pixelY): # TODO: Create a dictionary instead of printing
    image = Image.open(imgPath + imgList[imgNumber])
    exifData = image._getexif()
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
    print(pixelX)
    print(pixelY)