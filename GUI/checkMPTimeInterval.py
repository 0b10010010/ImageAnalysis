#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 22:03:49 2020

@author: spykat
"""

import numpy as np
from datetime import datetime, timezone


with open('MPData/VFR_HUD.txt') as file:
    for line in file:
        lists = [lines.strip() for lines in line.split(',')]
        t, timeValue = lists[0].split(':')
        dateTime = datetime.fromtimestamp(int(timeValue)/1e6, tz=timezone.utc)
        print(dateTime)