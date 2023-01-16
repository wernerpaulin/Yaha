#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

def init(PDI):
    pass

def update(PDI):
    PDI.count1 = PDI.count1 + 1

    #PDI.count1 = PDI.count1 + 1
    #PDI.var1 = PDI.var1 + 1
    #PDI.var2 = PDI.var2 + 1
    #PDI.var3 = PDI.var3 + 1
    
    PDI.selectText = PDI.selectGroup #selectStandard
    
    
    #print(PDI.checkboxgroup1)
    #print(PDI.checkboxgroup2)
    
    if (PDI.checkboxgroup1 == 1.0):
        PDI.checkboxgroup2 = 1.0
    
    #PDI.radiogroup1
    #PDI.checkboxgroup2
    #PDI.radiogroup2

    