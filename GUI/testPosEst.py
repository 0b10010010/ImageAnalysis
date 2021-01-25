#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 14:20:14 2020

@author: spykat
"""
from numpy import matrix, cos, sin, tan, pi, multiply, float64, divide

altitude = 339.42
altitude = 339.42 - 314 # in MSL (m)
altitude = 30
altitude *= 3.28084 # convert altitude to ft
heading = 357.0
latitude = 39.2029634
longitude =  -96.5453196
orientation = 3
angleOfViewX = 72.5852594569592
angleOfViewY = 51.97846716766602
imgW = 6000 
imgH = 4000
pixelX = 3771
pixelY = 2641

latlon = matrix([[latitude],[longitude]])

ab = matrix([[(2*altitude)/(cos(angleOfViewX/2))],[(2*altitude)/(cos(angleOfViewY/2))]])
img = matrix([[imgW],[imgH]])
scale = divide(ab, img)

# scale = matrix([[(2*altitude)/(imgW*(angleOfViewX/2))],[(2*altitude)/(imgH*(angleOfViewY/2))]])
offsetPix = matrix([[pixelX],[pixelY]])
offsetReal = multiply(scale, offsetPix)
rotation = matrix([[cos(heading), -sin(heading)], [sin(heading), cos(heading)]]) # rotate camera to NE world
posReal = rotation@offsetReal

lat = cos(latlon[0,0]*(pi/180))
lon = cos(latlon[1,0]*(pi/180))
dist2deg = (1/(lat*365228.16))
latlonTarget = latlon + divide(posReal,dist2deg)



# rotation = matrix([[cos(heading), sin(heading)], [-sin(heading), cos(heading)]]) # rotate camera to NE world
# offsetTargetCam = matrix([[pixelX-imgW/2],[pixelY-imgH/2]]) # in pixels
# offsetTargetNED = rotation.dot(offsetTargetCam) # rotated the camera to NE world frame
# scale = matrix([[(2/imgW)*altitude*tan(angleOfViewX/2)],[(2/imgH)*altitude*tan(angleOfViewY/2)]])
# offsetReal = multiply(offsetTargetNED, scale) # target offset in autopilot frame (ft)
# # targetReal = rotation.dot(offsetReal) # target offset in real world frame (ft)
# lat = cos(latlon[0,0]*(pi/180))
# lon = cos(latlon[1,0]*(pi/180))

# # ft2deg = matrix([[1/(lat*364286.0341)],[1/(lon*280162.91106970585)]])# convert distReal to degrees
# latlonTarget = latlon + (1/(lat*365228.16))*offsetReal
print(latlonTarget)

# objDist = array([[pixelX-imgW/2],[pixelY-imgH/2]]) # in pixels

# distReal = objDist*array([[(2/imgW)*altitude*tan(angleOfViewX/2)],[(2/imgH)*altitude*tan(angleOfViewY/2)]])
# rotation = array([[cos(heading), sin(heading)], [-sin(heading), cos(heading)]]) # NED frame

# latlon = array([[latitude],[longitude]])

# lat = cos(latlon[0]*(pi/180))
# lon = cos(latlon[1]*(pi/180))
# ft2deg = array([[1/(lat*364286.0341)],[1/(lon*280162.9111)]])# convert distReal to degrees
# latlonTarget = latlon + ft2deg*distReal

# # objectlatlon = latlon + (1/(lat*111321.543))*distReal

# scale = array([distReal[0]/imgH, distReal[1]/imgW])
# offsetTarget = array([scale[0]*pixelX, scale[1]*pixelY])

# mapRealtoCamera = array([[cos(heading), sin(heading)], [-sin(heading), cos(heading)]])
# posReal = mapRealtoCamera.dot(offsetTarget)
# targetGPS = array([posReal[0]/longitude, posReal[1]/latitude])