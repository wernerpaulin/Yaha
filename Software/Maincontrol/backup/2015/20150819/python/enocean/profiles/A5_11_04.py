#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *

''' EEP - device profile of radio telegrams definition '''
class A5_11_04():
    "EEP: Controller Status, Extended Lighting Status"
    def __init__(self):
        self.energy = 0
        self.operatingHours = 0

    def unpack(self, data, optData):
        print("TODO: A5_11_04 unpack")
        pass

    def pack(self, senderID = 'ffffff', destinationID = 'ffffff'):
        print("TODO: A5_11_04 pack")
        pass