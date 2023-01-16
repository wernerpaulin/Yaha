#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py
from __future__ import print_function		#Python 3 compatibility

from modules.sms.gsmmodem.modem import GsmModem

import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import logging
import core.modules.iosignal
import threading


PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
PIN = "0733" # SIM card PIN (if any)

SMS_TEXT_TRANSLATION_FILE = "/home/pi/Yaha/modules/sms/sms.tmx"

MODULE_CFG_FILE_NAME = "module.cfg.xml"
SMS_CFG_ELEMENT_NAME = "./subscribers/subscriber"
PROCESSTAG_ELEMENT_NAME = "processtag"
ACTION_TYPE_READ = "read"
ACTION_TYPE_WRITE = "write"

VALUE_TYPE_REAL = "REAL"
VALUE_TYPE_TEXT = "TEXT"

def init(PDI):
	global Subscribers
	
	Subscribers = dict()
	attrList = [] 
	subscriberID = None
	

	#read module configuration and initialize each burner
	try:
		cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
		cfgTree = xmlParser.parse(cfgFile)
		cfgRoot = cfgTree.getroot()

		#read configuration of switches
		for smsCfg in cfgRoot.findall(SMS_CFG_ELEMENT_NAME):
			try:
				#set up a switch manager for each switch found in the configuration
				subscriberID = smsCfg.get('id')
				Subscribers[subscriberID] = subscriberManager(PDI)
				
				#initialize settings parameter
				settingsNameList = getClassAttributes(Subscribers[subscriberID].settings)
				#try to find the corresponding entry in the configuration file 
				for settingName in settingsNameList:
					#get access to setting configuration:
					settingCfg = smsCfg.find('.//settings/setting[@name="' + settingName + '"]')
					#continue only if configuration exists
					if settingCfg != None:				
						setattr(Subscribers[subscriberID].settings, settingName, settingCfg.text)

				#notifications: initialize parameter
				notificationCfg = smsCfg.findall('.//notifications/notification')
				for notifcation in notificationCfg:
					Subscribers[subscriberID].notificationList.append(subNotification(PDI))
					#all parameters are optional. Therefore see which one are configured and set them in the class. If not configured the class will use default values
					for attr in notifcation.attrib:
						setattr(Subscribers[subscriberID].notificationList[-1], attr, notifcation.attrib[attr])
					
					#add process tag information
					processTagList = notifcation.findall(PROCESSTAG_ELEMENT_NAME) 
					#add processTags to IO signal
					for processTag in processTagList:
						#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
						attrList = []
						for attr in processTag.attrib:
							attrList.append(processTag.attrib[attr])
	
						#each IOsignal has an addProcessTag function: call it generically depending on ioName
						ioSignalInst = getattr(Subscribers[subscriberID].notificationList[-1], "processTag")			  #get access to IO signal
						ioSignalInst.addProcessTag(processTag.text, attrList)

				#commands: initialize parameter
				commandCfg = smsCfg.findall('.//commands/command')
				for command in commandCfg:
					commandKey = command.attrib["key"]
					#get information for each command
					Subscribers[subscriberID].commandList[commandKey] = subCommand(PDI)
					#each command has several actions
					actionCfg = command.findall("actions/action")
					for action in actionCfg:
						Subscribers[subscriberID].commandList[commandKey].actionItemList.append(subCommandActionItem(PDI))

						#all parameters are optional. Therefore see which one are configured and set them in the class. If not configured the class will use default values
						for attr in action.attrib:
							setattr(Subscribers[subscriberID].commandList[commandKey].actionItemList[-1], attr, action.attrib[attr])
						
						#add process tag information
						processTagList = action.findall(PROCESSTAG_ELEMENT_NAME) 
						#add processTags to IO signal
						for processTag in processTagList:
							#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
							attrList = []
							for attr in processTag.attrib:
								attrList.append(processTag.attrib[attr])
		
							#each IOsignal has an addProcessTag function: call it generically depending on ioName
							ioSignalInst = getattr(Subscribers[subscriberID].commandList[commandKey].actionItemList[-1], "processTag")			  #get access to IO signal
							ioSignalInst.addProcessTag(processTag.text, attrList)

				#initialize other variables
				Subscribers[subscriberID].translationMap = createTranslationMap(SMS_TEXT_TRANSLATION_FILE, Subscribers[subscriberID].settings.language)


			except Exception as e:
				print("Loading configuration for subscriber <{0}> failed: {1}".format(subscriberID, e))
				return	

	except Exception as e:
		print("Loading sms module configuration <{0}> failed: {1}".format(subscriberID, e))
		return	

	#initialize GSM modem if there is at least one subscriber
	if (len(Subscribers) > 0):
		initializeModem()

def initializeModem():
	try:
		modemHandlerThreadID = threading.Thread(target=modemInitThread)
		modemHandlerThreadID.start()
		return
	
	except Exception as e:
		print("GSM modem handler thread start failed: {0}".format(e))
		return  

def modemInitThread():
	global Modem

	#logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)		#uncomment if debugging information needed
	Modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=smsIncomingHandler)
	Modem.smsTextMode = False 		#must be False for UNICODE character support through sms
	Modem.connect(PIN)
	
	print('GSM Modem initialized')	
	try:	
		Modem.rxThread.join()
	finally:
		Modem.close();

def smsIncomingHandler(sms):
	global Subscribers
	#print('SMS message received\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
	#incoming SMS are interpreted as commands
	try:
		for subscriber in Subscribers:
			#1. Select subscriber based on the phone number
			if (Subscribers[subscriber].settings.phoneNumber == sms.number):
				#print("SMS from subscriber: {0} at {1}:\nCommand: {2}".format(subscriber, sms.time, sms.text))
				#2. Select command based on sms.text which represents the command key
				commandKey = str(sms.text).lower()
				if (commandKey in Subscribers[subscriber].commandList):
					#3. Execute actions (read/write) 
					replyText = ""
					for action in Subscribers[subscriber].commandList[commandKey].actionItemList:
						if (action.type == ACTION_TYPE_READ):
							replyText += (translateText(action.responseTextId + " " + convertValueToText(action.processTag.value(), action.readValueMap), Subscribers[subscriber].translationMap))
							replyText += "\n"
						elif (action.type == ACTION_TYPE_WRITE):
							if (action.writeValueType == VALUE_TYPE_REAL):
								action.processTag.value(float(action.writeValue))
							elif (action.writeValueType == VALUE_TYPE_TEXT):
								action.processTag.value(action.writeValue)
							else:
								print("writeValueType <{0}> is not supported for subscriber <{1}>")
						else:
							print("Action type <{0}> is not supported for subscriber <{1}>".format(action.writeValueType, subscriber))

					#Reply if there is text to reply
					if (len(replyText) > 0):
						print(replyText)
						sms.reply(replyText)

				else:
					sms.reply(translateText("$yaha_tuid:unknowncommand$: {0}".format(commandKey), Subscribers[subscriber].translationMap))

	except Exception as e:
		print("GSM modem smsIncomingHandler error: {0}".format(e))
		return  
		

def smsSendThread():
	global Modem
	"""
	Aufrufen wenn um Subscriber Update eine Notification ansteht: ModemHandlerThreadID.isAlive() abfragen
	"""
	try:
		pass
		#Modem.sendSms("+4366488653519", "Alarm central power up", waitForDeliveryReport=True)
	except Exception as e:
		print("GSM modem smsSendThread error: {0}".format(e))
		return  
	


def update(PDI):
	global Subscribers
	for subscriber in Subscribers:
		Subscribers[subscriber].update(PDI)


def convertValueToText(value, valueMapString):
	#valueMap: "0=$yaha_tuid:disarmed$,1=$yaha_tuid:armed$"
	try:
		valueMap = valueMapString.split(",")
		for map in valueMap:
			mapping = map.split("=")
			if (float(mapping[0]) == value):
				return mapping[1]
	except:
		return ""
		
	return ""

class subscriberManager:
	"Manages all subscription to this SMS module"
	#init
	def __init__(self, PDI):
		self.settings = subSettings(PDI)
		self.notificationList = []
		self.commandList = {}
		self.translationMap = {}
		
	#cyclic logic	
	def update(self, PDI):
		pass
		"""
		TODO notification:
		SMS mit Zeitstempel, Text (tmx!) und Value
		TMX
		Logic
		"""
	
class subSettings:
	'Subscription settings'
	#init
	def __init__(self, PDI):
		self.phoneNumber = None
		self.language = None

class subNotification:
	'Subscription notification'
	#init
	def __init__(self, PDI):
		self.riseEventValue = None
		self.fallEventValue = None
		self.riseTextId = None
		self.fallTextId = None
		self.processTag = core.modules.iosignal.IOsignal(PDI)

class subCommand:
	'Subscription command'
	#init
	def __init__(self, PDI):
		self.actionItemList = []
		

class subCommandActionItem:
	'Subscription command action item'
	#init
	def __init__(self, PDI):
		self.type = None
		self.responseTextId = None
		self.readValueMap = None
		self.writeValue = None
		self.writeValueType = None
		self.processTag = core.modules.iosignal.IOsignal(PDI)
        
#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]

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
                if (tuv.attrib[list(tuv.attrib.keys())[0]] == language):
                    #add this id and the corresponding text in the selected language to the dictionary
                    #translationMap[tu.get('tuid')] = tuv.find('seg').text
                    translationMap[tu.get('tuid')] = xmlParser.tostring(tuv.find('seg'), encoding="utf-8", method="text").strip()
                    translationMap[tu.get('tuid')] = translationMap[tu.get('tuid')].decode("utf-8")

    except Exception as e:
        print("createTranslationMap() error: {0}".format(e))
        translationMap.clear()

    return translationMap

def translateText(text, map):
    if (len(map) == 0):
        return text
    
    #try to replace all texts in the language map
    for id, langText in map.items():
         text = text.replace("$yaha_tuid:" + id + "$", str(langText)) #replace ID ($yaha_tuid:<id>$) in source text with text in requested language
  
    return text