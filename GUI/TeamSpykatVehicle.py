#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 17:59:54 2020

@author: spykat
"""

from dronekit import Vehicle

class SYSTEM_TIME(object):
    '''
        Read SYSTEM_TIME common message from mavlink over network (Image Analysis)
        laptop connected to Mission Planner laptop
    '''
    def __init__(self, time_usec=None, time_boot_us=None):
        '''
            SYSTEM_TIME object constructor
        '''
        self.time_unix_usec = time_usec
        self.time_boot_us = time_boot_us   
        
    def __str__(self):
        '''
            Return SYSTEM_TIME member in integer
        '''
        return 'SYSTEM_TIME:time_unix_usec={},time_boot_us={}'.format(self.time_unix_usec, self.time_boot_us)
    

class TeamSKVehicle(Vehicle):
    def __init__(self, *args):
        super(TeamSKVehicle, self).__init__(*args)

        # Create an instance of a class SYSTEM_TIME and initialize with None values
        self._system_time = SYSTEM_TIME()

        # Create a message listener using the decorator.   
        @self.on_message('SYSTEM_TIME')
        def listener(self, name, message):
            '''
                The listener is called for messages that contain the string specified in the decorator,
                passing the vehicle, message name, and the message.
                
                The listener writes the message to the (newly attached) ``vehicle.raw_imu`` object 
                and notifies observers.
            '''
            self._system_time.time_unix_usec = message.time_unix_usec
            self._system_time.time_boot_us = message.time_boot_ms

            # Notify all observers of new message (with new value)
            #   Note that argument `cache=False` by default so listeners
            #   are updated with every new message
            self.notify_attribute_listeners('system_time', self._system_time) 

    @property
    def system_time(self):
        return self._system_time