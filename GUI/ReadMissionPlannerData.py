#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 17:25:25 2019

@author: Alex Kim
"""

import requests
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class CamTrigWorker(QObject):
    # Use IP address of computer that's running mission planner:
    # 192.168.15.#:56781/mavlink/ where # should be the respective machine's IP
    # Refer to the following webpage
    # https://diydrones.com/forum/topics/forwarding-telemetry-data-not-the-mavlink-stream-from-mission
    def __init__(self):
        super().__init__()
        self.MPURL = 'http://MP_IPADDRESS/mavlink/' # TODO: Change this to respective IP Address of MP laptop

    @pyqtSlot
    def ReadMPMavlink():
        pass
