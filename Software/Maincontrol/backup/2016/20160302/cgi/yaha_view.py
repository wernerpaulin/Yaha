#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /usr/lib/cgi-bin/yaha_view.py

import cgi
import cgitb; cgitb.enable()
import json
import xml.etree.ElementTree as xmlParser
import os
import os.path
import sys
from time import gmtime, strftime


#process given data from client
cgiDataFromClient = cgi.FieldStorage()
language = ""
requestType = ""
moduleNameID = ""
moduleNameList = {'empty': 0}    #force creating a dictionary
moduleNameList.clear()           #clear dictionary immediately
translationMap = {'empty': 0}    #force creating a dictionary
translationMap.clear()           #clear dictionary immediately
availableLanguages = {'empty': 0}    #force creating a dictionary
availableLanguages.clear()           #clear dictionary immediately


YAHA_VIEW_MODULE_PATH = '/var/www/yaha/modules'
YAHA_LANGUAGE_DEFINITION_FILE = '/var/www/yaha/core/languages/languages.tmx'


#creates a dictionary to map a ID to a text in a certain language
def createTranslationMap(file, language):
    translationMap = {'empty': 0}    #force creating a dictionary
    translationMap.clear()           #clear dictionary immediately

    #access tmx file
    try:
        tmxTree = xmlParser.parse(file)
        tmxRoot = tmxTree.getroot()
        tmxBody = tmxRoot.find('body')

        #go through all text units which can be translated and build up a dictionary: ID:text
        for tu in tmxBody:
            #go through all languages which exists for this text and select the one according the requested language
            for tuv in tu:
                #languages is a attribute with namespace: ignore namespace and just look out for language code: de, en,..
                if (tuv.attrib[tuv.attrib.keys()[0]] == language):
                    #add this id and the corresponding text in the selected language to the dictionary
                    #translationMap[tu.get('tuid')] = tuv.find('seg').text
                    translationMap[tu.get('tuid')] = xmlParser.tostring(tuv.find('seg'), encoding="utf-8", method="text")

    except Exception, e:
        #print e
        translationMap.clear()

    return translationMap

def translateText(text, map):
    #try to replace all texts in the language map
    for id, langText in map.iteritems():
         text = text.replace("$yaha_tuid:" + id + "$", langText) #replace ID ($yaha_tuid:<id>$) in source text with text in requested language
  
    return text


#initialize reply    
print "Content-type:text/html\r\n"  #mandatory header for CGI call backs

#find out what the client needs (request type)
try:
    requestType = cgiDataFromClient["requestType"].value
except:
    pass

#in which language?
#language codes according to: http://www.iana.org/assignments/language-subtag-registry/language-subtag-registry
try:
    language = cgiDataFromClient["language"].value  
except:
    language = "en"    #fallback is English


#Name of module?
try:
    moduleNameID = cgiDataFromClient["moduleNameID"].value
    #create translation map from ID to requested language
    translationMap = createTranslationMap(YAHA_VIEW_MODULE_PATH + '/' + moduleNameID + '/' + moduleNameID + '.tmx', language)
except:
    translationMap.clear()


#prepare reply
if (requestType == "getModuleList"):
    moduleNameList.clear()      #clear any old content
    
    #a Yaha module needs to be located in the modules directory
    #the name of the directory is assumed as module name ID
    #the name of the content file (.mod) must have the same name as the directory
    for item in os.listdir(YAHA_VIEW_MODULE_PATH):
        path = os.path.join(YAHA_VIEW_MODULE_PATH, item)
        
        #ignore all files, just go for directories
        if os.path.isdir(path):
            try:
                moduleNameID = os.path.basename(item)
                
                #access module
                moduleTree = xmlParser.parse(path + '/' + moduleNameID + '.mod')
                moduleRoot = moduleTree.getroot()
                #access module info
                moduleInfo = moduleRoot.find('info')
    
                #create translation map from ID to requested language (need to be created here because no module is given => to be created for every module
                translationMap = createTranslationMap(path + '/' + moduleNameID + '.tmx', language)
                moduleNameList[moduleNameID] = [moduleInfo.find('icon').text, translateText(moduleInfo.find('name').text, translationMap)]  #inline translation of module name
            except:
                continue

    #reply to client in json format
    print json.dumps(moduleNameList)
    
elif (requestType == "getModuleContent"):
    #read entire file and send it to client: xml parsing happens at the client as info section is used at the client (not only html data)
    file = open(YAHA_VIEW_MODULE_PATH + '/' + moduleNameID + '/' + moduleNameID + '.mod', 'r')
    xml_data = file.read()
    print translateText(xml_data, translationMap)
    
elif (requestType == "getAvailableLanguages"):
    #{"en": "English", "de": "Deutsch"};
    #availableLanguages["en"] = "English"
    #availableLanguages["de"] = "Deutsch"

    availableLanguages.clear()
    
    #access tmx file
    try:
        tmxTree = xmlParser.parse(YAHA_LANGUAGE_DEFINITION_FILE)
        tmxRoot = tmxTree.getroot()
        tmxBody = tmxRoot.find('body')

        #go through all text units - in this file only one exists though
        for tu in tmxBody:
            #go through all languages which are defined
            for tuv in tu:
                #languages is a attribute with namespace: ignore namespace and just look out for language code: de, en,..
                #language code: tuv.attrib[tuv.attrib.keys()[0]]
                #language name: xmlParser.tostring(tuv.find('seg'), encoding="utf-8", method="text")
                availableLanguages[tuv.attrib[tuv.attrib.keys()[0]]] = xmlParser.tostring(tuv.find('seg'), encoding="utf-8", method="text")

    except Exception, e:
        #print e
        availableLanguages.clear()

    #reply to client in json format
    print json.dumps(availableLanguages)
    
elif (requestType == "getDateTime"):
    print strftime("%d.%m.%Y.%H.%M.%S", gmtime())

    