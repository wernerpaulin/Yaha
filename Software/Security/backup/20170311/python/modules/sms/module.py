#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py
from __future__ import print_function		#Python 3 compatibility

from modules.sms.gsmmodem.modem import GsmModem

import os, sys
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
	global SmsSendThreadID
	global ModemInitializedFlag
	
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
					Subscribers[subscriberID].notifications.addNotification()
					#all parameters are optional. Therefore see which one are configured and set them in the class. If not configured the class will use default values
					for attr in notifcation.attrib:
						setattr(Subscribers[subscriberID].notifications.list[-1], attr, notifcation.attrib[attr])
					
					#add process tag information
					processTagList = notifcation.findall(PROCESSTAG_ELEMENT_NAME) 
					#add processTags to IO signal
					for processTag in processTagList:
						#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
						attrList = []
						for attr in processTag.attrib:
							attrList.append(processTag.attrib[attr])
	
						#each IOsignal has an addProcessTag function: call it generically depending on ioName
						ioSignalInst = getattr(Subscribers[subscriberID].notifications.list[-1], "processTag")			  #get access to IO signal
						ioSignalInst.addProcessTag(processTag.text, attrList)
						

				#commands: initialize parameter
				commandCfg = smsCfg.findall('.//commands/command')
				for command in commandCfg:
					commandKey = command.attrib["key"]
					#get information for each command
					Subscribers[subscriberID].commands.addCommand(commandKey)
					#each command has several actions
					actionCfg = command.findall("actions/action")
					for action in actionCfg:
						Subscribers[subscriberID].commands.list[commandKey].addAction()

						#all parameters are optional. Therefore see which one are configured and set them in the class. If not configured the class will use default values
						for attr in action.attrib:
							setattr(Subscribers[subscriberID].commands.list[commandKey].actions[-1], attr, action.attrib[attr])
						
						#add process tag information
						processTagList = action.findall(PROCESSTAG_ELEMENT_NAME) 
						#add processTags to IO signal
						for processTag in processTagList:
							#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
							attrList = []
							for attr in processTag.attrib:
								attrList.append(processTag.attrib[attr])
		
							#each IOsignal has an addProcessTag function: call it generically depending on ioName
							ioSignalInst = getattr(Subscribers[subscriberID].commands.list[commandKey].actions[-1], "processTag")			  #get access to IO signal
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
		#start modem
		ModemInitializedFlag = False
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
	global Subscribers
	global ModemInitializedFlag

	#logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)		#uncomment if debugging information needed
	Modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=smsIncomingHandler)
	Modem.smsTextMode = False 		#must be False for UNICODE character support through sms
	Modem.connect(PIN)
	
	ModemInitializedFlag = True
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
				Subscribers[subscriber].commandStack.append(commandKey)
				
	except Exception as e:
		print("GSM modem smsIncomingHandler error: {0} in line {1}".format(e, sys.exc_info()[-1].tb_lineno))
		return  
		

def smsSendThread():
	global Modem
	global Subscribers
	global ModemInitializedFlag

	#wait until modem is operational
	if (ModemInitializedFlag != True):
		return

	try:
		#go through each subscriber and check whether there is a text to send => send one sms (no while to not stress the modem)
		for subscriber in Subscribers:
			if (len(Subscribers[subscriber].smsSendQueue) > 0):
				Modem.sendSms(Subscribers[subscriber].settings.phoneNumber, Subscribers[subscriber].smsSendQueue.pop(0), waitForDeliveryReport=True)
	except Exception as e:
		print("GSM modem smsSendThread error: {0}".format(e))
		try:
			Modem.close()
		except Exception as e:
			print("GSM modem close error: {0}".format(e))

		try:
			initializeModem()
		except Exception as e:
			print("GSM modem re-init error: {0}".format(e))
		

	


def update(PDI):
	global Subscribers
	
	try:
		for subscriber in Subscribers:
			Subscribers[subscriber].update(PDI)
	except Exception as e:
		print("SMS module update error: {0} in line {1}".format(e, sys.exc_info()[-1].tb_lineno))

def convertValueToText(value, valueMapString):
	#valueMap: "0=$yaha_tuid:disarmed$,1=$yaha_tuid:armed$"
	try:
		valueMap = valueMapString.split(",")
		for map in valueMap:
			mapping = map.split("=")
			if (float(mapping[0]) == value):
				return mapping[1]
	except:
		return value
		
	return value

class subscriberManager:
	"Manages all subscription to this SMS module"
	#init
	def __init__(self, PDI):
		self.settings = subSettings(PDI)
		self.notifications = subNotifications(PDI)
		self.commands = subCommands(PDI)
		self.translationMap = {}
		self.commandStack = []
		self.smsSendQueue = []
		
	#cyclic logic	
	def update(self, PDI):
		#command execution
		if len(self.commandStack) > 0:
			commandKey = self.commandStack.pop(0)
			
			replyText = ""
			if (commandKey in self.commands.list):
				#3. Execute actions (read/write) 
				for action in self.commands.list[commandKey].actions:
					if (action.type == ACTION_TYPE_READ):
						replyText += (translateText(action.responseTextId + " " + str(convertValueToText(action.processTag.value(), action.valueMap)), self.translationMap))
						replyText += "\n"
					elif (action.type == ACTION_TYPE_WRITE):
						if (action.writeValueType == VALUE_TYPE_REAL):
							action.processTag.value(float(action.writeValue))
						elif (action.writeValueType == VALUE_TYPE_TEXT):
							action.processTag.value(action.writeValue)
						else:
							print("writeValueType <{0}> is not supported for subscriber <{1}>")
					else:
						print("Action type <{0}> is not supported for subscriber <{1}>".format(action.writeValueType, self.settings.phoneNumber))

			else:
				replyText = translateText("$yaha_tuid:unknowncommand$: {0}".format(commandKey), self.translationMap) 

			#Reply if there is text to reply
			if (len(replyText) > 0):
				print(replyText)
				self.smsSendQueue.append(replyText)

		replyText = ""
		#notifications
		for notification in self.notifications.list:
			#edge detection
			if (notification.processTag.value() != notification.oldValue):
				notification.oldValue = notification.processTag.value()

				#rise trigger value defined => only notify if this value is now 
				if (notification.riseEventValue != None):
					replyText += (translateText(notification.responseTextId + " " + str(convertValueToText(notification.processTag.value(), notification.valueMap)), self.translationMap))					
				#fall trigger value defined => only notify if this value is now 
				elif (notification.fallEventValue != None):
					replyText += (translateText(notification.responseTextId + " " + str(convertValueToText(notification.processTag.value(), notification.valueMap)), self.translationMap))					
				#no trigger value defined =>notify any change 
				else:
					replyText += (translateText(notification.responseTextId + " " + str(convertValueToText(notification.processTag.value(), notification.valueMap)), self.translationMap))					

				#Reply if there is text to reply
				"""
				TODO notification:
				Fehler beim Senden nach Init! Funktioniert Init-Flag?
				Text formatieren
				Zeitstempel einbauen (kürzen): 160 Zeichen!
				
				Funtkionstest ob Flanken/Change-Erkennung funktioniert inkl. Value Map
				read Config bei Commands deaktivieren
				"""		
				print("TODO: Notifications noch nicht fertig!")
				
				if (len(replyText) > 0):
					print(replyText)
					#self.smsSendQueue.append("CHANGE")
					break
					
			



		#before starting another sms send thread, check whether the old one has been terminated (= thread function finished)
		try:
			if (SmsSendThreadID.isAlive() == True):
				return
		except:
			#thread handle invalid = thread not yet started => also ok. Continue with starting a new thread
			pass
		
		try:
			#set up send thread if something is in the queue to avoid blocking which continuously checks whether there are messages to send
			if len(self.smsSendQueue) > 0:
				SmsSendThreadID = threading.Thread(target=smsSendThread)
				SmsSendThreadID.start()

			return
		except Exception as e:
			print("SMS starting send thread failed: {0}".format(e))
			return  



		

	
class subSettings:
	'Subscription settings'
	#init
	def __init__(self, PDI):
		self.phoneNumber = None
		self.language = None

class subNotifications:
	'Subscription notifications'
	#init
	def __init__(self, PDI):
		self.PDI = PDI
		self.list = []

	def addNotification(self):
		self.list.append(subNotificationItem(self.PDI))


class subNotificationItem:
	'Subscription notification item'
	#init
	def __init__(self, PDI):
		self.riseEventValue = None
		self.fallEventValue = None
		self.responseTextId = None
		self.valueMap = None
		self.oldValue = None
		self.processTag = core.modules.iosignal.IOsignal(PDI)

class subCommands:
	'Subscription commands'
	#init
	def __init__(self, PDI):
		self.PDI = PDI
		self.list = {}

	def addCommand(self, key):
		self.list[key] = subCommandActions(self.PDI)
	
		
class subCommandActions:
	'Subscription command'
	#init
	def __init__(self, PDI):
		self.PDI = PDI
		self.actions = []
	
	def addAction(self):
		self.actions.append(subCommandActionItem(self.PDI))

class subCommandActionItem:
	'Subscription command action item'
	#init
	def __init__(self, PDI):
		self.type = None
		self.responseTextId = None
		self.valueMap = None
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