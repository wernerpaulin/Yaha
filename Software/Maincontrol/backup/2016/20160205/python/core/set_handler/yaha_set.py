#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]

class main:
    'Yaha settings manager: loads and saves PDI values to xml files'

    def __init__(self, path, pdi):
        self.path = path
        self.PDI = pdi
        
        print("yaha_set: weiter machen: create ähnl. wie altes save. Dann load/save: local testen. Dann die Handler wie früher programmieren")
        
        '''
        IO-Typ von PDI umbenennen in isSettings: Python, Excel = xml neu generieren
        Als Owner das jeweilige Modul eintragen
        Beim Laden von Settings: ActiveSettings.xml aktualisieren (zuerst)

        yaha_data: GetSettingTags()
        1. Loop: try: getAttribute PDI ProcessTag
        2. Write / Load
        '''
    
    def load(self):
        pass
    
    def loadHandler(self):
        pass
    
    def save(self):
        pass
    
    def saveHandler(self):
        pass
    
    def create(self):
        pass
    
    def createHandler(self):
        pass
    
    def list(self):
        pass
    
