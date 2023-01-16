#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /usr/lib/cgi-bin/yaha_view.py

import cgi
import cgitb; cgitb.enable()
import json
import xml.etree.ElementTree as xmlParser
import os
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


YAHA_VIEW_MODULE_DATA_PATH = '/var/www/modules/'
YAHA_VIEW_TMX_PATH = '/var/www/tmx/'
YAHA_LANGUAGE_DEFINITION_FILE = 'languages.tmx'


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
    translationMap = createTranslationMap(YAHA_VIEW_TMX_PATH + moduleNameID + ".tmx", language)
except:
    translationMap.clear()





#prepare reply
if (requestType == "getModuleList"):
    moduleNameList.clear()      #clear any old content
    
    for file in os.listdir(YAHA_VIEW_MODULE_DATA_PATH):
        if file.endswith(".mod"):
            moduleNameID = os.path.splitext(os.path.basename(file))[0]        #.basename() cuts the directory, .splitext() cuts the extensions and the filename

            #access module
            moduleTree = xmlParser.parse(YAHA_VIEW_MODULE_DATA_PATH + file)
            moduleRoot = moduleTree.getroot()
            #access module info
            moduleInfo = moduleRoot.find('info')

            #create translation map from ID to requested language (need to be created here because no module is given => to be created for every module
            translationMap = createTranslationMap(YAHA_VIEW_TMX_PATH + moduleNameID + ".tmx", language)
            moduleNameList[moduleNameID] = [moduleInfo.find('icon').text, translateText(moduleInfo.find('name').text, translationMap)]  #inline translation of module name

    #reply to client in json format
    print json.dumps(moduleNameList)
    
elif (requestType == "getModuleContent"):
    #access module
    moduleTree = xmlParser.parse(YAHA_VIEW_MODULE_DATA_PATH + moduleNameID + ".mod")
    moduleRoot = moduleTree.getroot()
    #access html data
    html_data = moduleRoot.find('html_data')
    #reply to client with html data
    #print translateText(html_data.text, translationMap)
    print translateText(xmlParser.tostring(html_data, encoding="utf-8", method="text"), translationMap)

elif (requestType == "getAvailableLanguages"):
    #{"en": "English", "de": "Deutsch"};
    #availableLanguages["en"] = "English"
    #availableLanguages["de"] = "Deutsch"

    availableLanguages.clear()
    
    #access tmx file
    try:
        tmxTree = xmlParser.parse(YAHA_VIEW_TMX_PATH + YAHA_LANGUAGE_DEFINITION_FILE)
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

elif (requestType == "setDateTime"):
    try:
        setTime = cgiDataFromClient["setTime"].value
        setDate = cgiDataFromClient["setDate"].value

        #os.system('sudo date -s "2004-02-29 16:21:42"')
        os.system('sudo date -s "' + setDate + ' ' + setTime + ':00"')     #call system shell function: sudo date -s "2004-02-29 16:21:42"

        #send back current date and time for immediate update
        print strftime("%d.%m.%Y.%H.%M.%S", gmtime()) 
    except Exception, e:
        #print e
        pass