#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import xycurvelin

import core.modules.iosignal
from core.modules.cal_event import *

MODULE_CFG_FILE_NAME = "module.cfg.xml"
LIN_CURVE_CFG_ELEMENT_NAME = "./sensors/linearizationcurves/linearizationcurve"


def init(PDI):
    global LinCurves
    LinCurves = dict()
    attrList = []  


    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()


        #read configuration of group control
        for linCurveCfg in cfgRoot.findall(LIN_CURVE_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                curveID = linCurveCfg.get('id')
                LinCurves[curveID] = LinearizationWrapper(PDI)
                LinCurves[curveID].curveID = curveID


                #initialize window parameter
                pointPairCfg = linCurveCfg.findall('.//pointpairs/pointpair')
                for pointPair in pointPairCfg:
                    LinCurves[curveID].curveData.addPointPair(float(pointPair.attrib['x']), float(pointPair.attrib['y']))        

            except Exception, e:
                print("Loading configuration for curve <{0}> failed: {1}".format(curveID, e))
                return    
        
    
            '''
            WEITER MACHEN:
            Sensoren auslesen und mit Lin curve verlinken
            Im zyklischen Teil über alle Sensoren loopen (ioPoint und Linearisierung berechnen)
            '''
    
    except Exception, e:
        print("Loading module configuration <{0}> for heating control: {1}".format(MODULE_CFG_FILE_NAME,e))
        return



def update(PDI):
    global LinCurves

    #handle all groups to control several blinds at once
    'UNNÖTIG'
    for linCurve in LinCurves:
        LinCurves[linCurve].update(PDI)



class LinearizationWrapper:
    "Does the linearization and conversion of all temperature sensors"
   
    #init
    def __init__(self, PDI):
        self.curveID = None
        self.curveData = xycurvelin.chartLin()

    'UNNÖTIG'
    #cyclic linearization    
    def update(self, PDI):
        pass


