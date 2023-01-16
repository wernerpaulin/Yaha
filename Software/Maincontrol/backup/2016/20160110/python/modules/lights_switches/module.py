#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

def init(PDI):
    print("### DEBUGGING: module.py / light_switches")

def update(PDI):
    #Light 1: ON
    if (PDI.light1on == 1):
        PDI.light1on = 0
        PDI.ioLight1offOn = 1

    #Light 1: OFF
    if (PDI.light1off == 1):
        PDI.light1off = 0
        PDI.ioLight1offOn = 0
    
    #Light 1: TEACH
    if (PDI.light1teach == 1):
        PDI.light1teach = 0
        PDI.ioLight1teach = 1
    else:
        PDI.ioLight1teach = 0

    #Light 2: ON
    if (PDI.light2on == 1):
        PDI.light2on = 0
        PDI.ioLight2offOn = 1

    #Light 2: OFF
    if (PDI.light2off == 1):
        PDI.light2off = 0
        PDI.ioLight2offOn = 0
    
    #Light 2: TEACH
    if (PDI.light2teach == 1):
        PDI.light2teach = 0
        PDI.ioLight2teach = 1
    else:
        PDI.ioLight2teach = 0
