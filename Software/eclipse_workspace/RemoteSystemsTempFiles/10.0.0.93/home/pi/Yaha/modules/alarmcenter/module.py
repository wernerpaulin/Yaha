#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
ALARMCENTER_CFG_ELEMENT_NAME = "./alarmcenters/alarmcenter"
PROCESSTAG_ELEMENT_NAME = "processtag"

IO_SIMULATION_ACTIVE_PDI_TAG = "ioSimulation"

ALARM_CENTER_OPERATING_MODE_MANUAL = 0
ALARM_CENTER_OPERATING_MODE_AUTOMATIC = 1

ALARM_CENTER_STATE_DISARMED = 0
ALARM_CENTER_STATE_GETTING_ARMED = 1
ALARM_CENTER_STATE_ARMED = 2

ZONE_STATE_DISABLED = 0
ZONE_STATE_NO_ALARM = 1
ZONE_STATE_ALARM = 2

def init(PDI):
	global Alarmcenters
	
	Alarmcenters = dict()
	attrList = [] 
	alarmcenterID = None
	
	#read module configuration and initialize each alarm center
	try:
		cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
		cfgTree = xmlParser.parse(cfgFile)
		cfgRoot = cfgTree.getroot()

		#read configuration of switches
		for alarmCenterCfg in cfgRoot.findall(ALARMCENTER_CFG_ELEMENT_NAME):
			try:
				#set up a switch manager for each switch found in the configuration
				alarmcenterID = alarmCenterCfg.get('id')
				Alarmcenters[alarmcenterID] = alarmCenterManager(PDI)	

				#initialize inputs: get generically all inputs which are defined
				ioNameList = getClassAttributes(Alarmcenters[alarmcenterID].inputs)
				#try to find the corresponding PDI mapping in the configuration file 
				for ioName in ioNameList:
					#get access to input configuration: <input name="switchedOn">
					inputCfg = alarmCenterCfg.find('.//inputs/input[@name="' + ioName + '"]')
					if inputCfg != None:
						#get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
						processTagList = inputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
						#add processTags to IO signal
						for processTag in processTagList:
							#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
							attrList = []
							for attr in processTag.attrib:
								attrList.append(processTag.attrib[attr])
		
							#each IOsignal has an addProcessTag function: call it generically depending on ioName
							ioSignalInst = getattr(Alarmcenters[alarmcenterID].inputs, ioName)			  #get access to IO signal: "on", "off",...
							ioSignalInst.addProcessTag(processTag.text, attrList)

				#initialize inputs: get generically all outputs which are defined
				ioNameList = getClassAttributes(Alarmcenters[alarmcenterID].outputs)
				#try to find the corresponding PDI mapping in the configuration file 
				for ioName in ioNameList:
					#get access to input configuration: <input name="switchedOn">
					outputCfg = alarmCenterCfg.find('.//outputs/output[@name="' + ioName + '"]')
					if outputCfg != None:
						#get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
						processTagList = outputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
						#add processTags to IO signal
						for processTag in processTagList:
							#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
							attrList = []
							for attr in processTag.attrib:
								attrList.append(processTag.attrib[attr])
		
							#each IOsignal has an addProcessTag function: call it generically depending on ioName
							ioSignalInst = getattr(Alarmcenters[alarmcenterID].outputs, ioName)			  #get access to IO signal: "on", "off",...
							ioSignalInst.addProcessTag(processTag.text, attrList)

				#initialize settings parameter
				settingsNameList = getClassAttributes(Alarmcenters[alarmcenterID].settings)
				#try to find the corresponding entry in the configuration file 
				for settingName in settingsNameList:
					#get access to input configuration: <statusitem name="ontime">
					settingCfg = alarmCenterCfg.find('.//settings/setting[@name="' + settingName + '"]')
					#continue only if configuration exists
					if settingCfg != None:
						setattr(Alarmcenters[alarmcenterID].settings, settingName, float(settingCfg.text))

				#initialize operating modes parameter
				#switch
				operatingSwitchCfg = alarmCenterCfg.find('.//operatingmodes/switch')
				if operatingSwitchCfg != None:				
					#get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
					processTagList = operatingSwitchCfg.findall(PROCESSTAG_ELEMENT_NAME) 
					#add processTags to IO signal
					for processTag in processTagList:
						#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
						attrList = []
						for attr in processTag.attrib:
							attrList.append(processTag.attrib[attr])
	
						#each IOsignal has an addProcessTag function: call it generically depending on ioName
						ioSignalInst = getattr(Alarmcenters[alarmcenterID].operatingModes, "switch")			  #get access to IO signal: "up", "down",...
						ioSignalInst.addProcessTag(processTag.text, attrList)
				
				
				#modes
				operatingModeNameList = getClassAttributes(Alarmcenters[alarmcenterID].operatingModes.types)	  #['automatic', ...]
				#try to find the corresponding entry in the configuration file 
				for operatingModeName in operatingModeNameList:
					operatingModeCfg = alarmCenterCfg.find('.//operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
					#continue only if configuration exists
					if operatingModeCfg != None:
						#access operating mode infrastructure and initialize interfaces
						operatingModeObj = getattr(Alarmcenters[alarmcenterID].operatingModes.types, operatingModeName)
						interfaceNameList = getClassAttributes(operatingModeObj)	  #['setTemperature', ...]
						#try to find settings for all found interfaces
						for interfaceName in interfaceNameList:
							interfaceCfg = alarmCenterCfg.find('.//operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
							#continue only if configuration exists
							if interfaceCfg != None:				
								#get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
								processTagList = interfaceCfg.findall(PROCESSTAG_ELEMENT_NAME) 
								#add processTags to IO signal
								for processTag in processTagList:
									#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
									attrList = []
									for attr in processTag.attrib:
										attrList.append(processTag.attrib[attr])
				
									#each IOsignal has an addProcessTag function: call it generically depending on ioName
									ioSignalInst = getattr(operatingModeObj, interfaceName)			  #get access to IO signal: "up", "down",...
									ioSignalInst.addProcessTag(processTag.text, attrList)


				#initialize status points
				ioNameList = getClassAttributes(Alarmcenters[alarmcenterID].status)	  #['state', ...]
				#try to find the corresponding PDI mapping in the configuration file 
				for ioName in ioNameList:
					#get access to input configuration: <statusitem name="ontime">
					statusCfg = alarmCenterCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
					#continue only if configuration exists
					if statusCfg != None:
						#get all mapped PDI process tags: <processtag>xxx</processtag>
						processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
						#add processTags to IO signal
						for processTag in processTagList:
							#each IOsignal has an addProcessTag function: call it generically depending on ioName
							ioSignalInst = getattr(Alarmcenters[alarmcenterID].status, ioName)			  #get access to IO signal: "state", "setTemperature",...
							ioSignalInst.addProcessTag(processTag.text, None)
			
				
				try:
					#read configuration of zones
					for zoneCfg in alarmCenterCfg.findall('.//zones/zone'):
						#set up a switch manager for each switch found in the configuration
						zoneID = zoneCfg.get('id')
						Alarmcenters[alarmcenterID].zones[zoneID] = alarmCenterZone(PDI)	
						
						#initialize inputs: get generically all inputs which are defined
						ioNameList = getClassAttributes(Alarmcenters[alarmcenterID].zones[zoneID].inputs)
						#try to find the corresponding PDI mapping in the configuration file 
						for ioName in ioNameList:
							#get access to input configuration: <input name="switchedOn">
							inputCfg = zoneCfg.find('./inputs/input[@name="' + ioName + '"]')
							if inputCfg != None:
								#get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
								processTagList = inputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
								#add processTags to IO signal
								for processTag in processTagList:
									#convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
									attrList = []
									for attr in processTag.attrib:
										attrList.append(processTag.attrib[attr])
				
									#each IOsignal has an addProcessTag function: call it generically depending on ioName
									ioSignalInst = getattr(Alarmcenters[alarmcenterID].zones[zoneID].inputs, ioName)			  #get access to IO signal: "on", "off",...
									ioSignalInst.addProcessTag(processTag.text, attrList)
					
						#initialize status points
						ioNameList = getClassAttributes(Alarmcenters[alarmcenterID].zones[zoneID].status)	  #['state', ...]
						#try to find the corresponding PDI mapping in the configuration file 
						for ioName in ioNameList:
							#get access to input configuration: <statusitem name="ontime">
							statusCfg = zoneCfg.find('./statusitems/statusitem[@name="' + ioName + '"]')
							#continue only if configuration exists
							if statusCfg != None:
								#get all mapped PDI process tags: <processtag>xxx</processtag>
								processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
								#add processTags to IO signal
								for processTag in processTagList:
									#each IOsignal has an addProcessTag function: call it generically depending on ioName
									ioSignalInst = getattr(Alarmcenters[alarmcenterID].zones[zoneID].status, ioName)			  #get access to IO signal: "state", "setTemperature",...
									ioSignalInst.addProcessTag(processTag.text, None)

						
				except Exception as e:
					print("Loading configuration for zone <{0}> in alarm center <{1}> failed: {2}".format(zoneID, alarmcenterID, e))
					return	

			except Exception as e:
				print("Loading configuration for alarm center <{0}> failed: {1}".format(alarmcenterID, e))
				return	

	except Exception as e:
		print("Loading alarm center module configuration <{0}> failed: {1}".format(alarmcenterID, e))
		return	

def update(PDI):
	global Alarmcenters

	for alarmcenter in Alarmcenters:
		Alarmcenters[alarmcenter].update(PDI)

class alarmCenterManager:
	"Manages all alarm centers"
	#init
	def __init__(self, PDI):
		self.inputs = alarmCenterInputs(PDI)
		self.outputs = alarmCenterOutputs(PDI)
		self.settings = alarmCenterSettings(PDI)
		self.operatingModes = alarmCenterOperatingModes(PDI)
		self.status = alarmCenterStatus(PDI)
		self.zones = dict()
		self.oldAlarmCenterState = None
		self.alarmLight = alarmSignalManager()
		self.alarmSound = alarmSignalManager()
		self.samplingTime = 0
		self.lastCallTime = 0
	
	#cyclic logic	
	def update(self, PDI):
		#cycle time calculation
		self.samplingTime = max(time.time() - self.lastCallTime, 0)
		self.lastCallTime = time.time()
		
		#depending on operation mode generate operating mode
		#manual mode
		if (self.operatingModes.switch.value() == ALARM_CENTER_OPERATING_MODE_MANUAL):
			#trigger -> manipulate switch
			if (self.operatingModes.types.manual.armStartTrigger.value() == 1):
				self.operatingModes.types.manual.armStartTrigger.value(0)
				self.operatingModes.types.manual.armEnableSwitch.value(1)
				self.status.state.value(ALARM_CENTER_STATE_GETTING_ARMED)
			
			#trigger -> manipulate switch
			elif (self.operatingModes.types.manual.armEndTrigger.value() == 1):
				self.operatingModes.types.manual.armEndTrigger.value(0)
				self.operatingModes.types.manual.armEnableSwitch.value(0)
				self.status.state.value(ALARM_CENTER_STATE_DISARMED)
			
			else:
				#switch is operated by UI and defines the alarm center state
				if (self.operatingModes.types.manual.armEnableSwitch.value() == 1):
					self.status.state.value(ALARM_CENTER_STATE_GETTING_ARMED)
				else:
					self.status.state.value(ALARM_CENTER_STATE_DISARMED)
			
		#automatic mode
		else:
			try:
				#convert start and end time string into a time object
				startTime = time.strptime(self.operatingModes.types.automatic.armStartTime.value(), '%H:%M')
				endTime = time.strptime(self.operatingModes.types.automatic.armEndTime.value(), '%H:%M')
				
				#remove date information of current time because comparison would fail as start and end time have no date
				currentTimeString = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute)
				currentTime = time.strptime(currentTimeString, '%H:%M')
				
				#check whether current time is within arm phase
				#normal: e.g. from 08:00 to 20:00
				if (endTime >= startTime):
					if (startTime <= currentTime <= endTime):
						self.status.state.value(ALARM_CENTER_STATE_GETTING_ARMEDARMED)
					else:
						self.status.state.value(ALARM_CENTER_STATE_DISARMED)
				#over midnight: from 23:00 to 06:00
				else:
					beforeMidnightTime = time.strptime("23:59", '%H:%M')
					midnightTime = time.strptime("00:01", '%H:%M')					

					if (startTime <= currentTime <= beforeMidnightTime) or (midnightTime <= currentTime < endTime):
						self.status.state.value(ALARM_CENTER_STATE_GETTING_ARMED)
					else:
						self.status.state.value(ALARM_CENTER_STATE_DISARMED)
			except Exception as e:
				print("Alarm center automatic mode configuration error: {0}".format(e))
				self.status.state.value(ALARM_CENTER_STATE_DISARMED)

		#light indicator when alarm center has been changed
		if (self.oldAlarmCenterState != self.status.state.value()):
			if (self.status.state.value() == ALARM_CENTER_STATE_ARMED) or (self.status.state.value() == ALARM_CENTER_STATE_GETTING_ARMED):
				self.alarmLight.activate(offDelay=self.settings.shortFlashTime, onDelay=None)
			elif (self.status.state.value() == ALARM_CENTER_STATE_DISARMED):
				self.alarmLight.deactivate()
				self.alarmSound.deactivate()				
			
			self.oldAlarmCenterState = self.status.state.value()

		#delayed change to arm state
		if (self.status.state.value() == ALARM_CENTER_STATE_GETTING_ARMED):
			self.outputs.armCountDown.value(self.outputs.armCountDown.value() - self.samplingTime)
			if (self.outputs.armCountDown.value() <= 0):
				self.status.state.value(ALARM_CENTER_STATE_ARMED)
		else:
			self.outputs.armCountDown.value(self.settings.delayToBeArmed)

		#handle zones
		for zoneID in self.zones:
			self.zones[zoneID].alarmCenterState = self.status.state.value()
			self.zones[zoneID].alarmCenterGlobalAlarmOff = self.inputs.alarmOffTrigger.value()
			self.zones[zoneID].update()
			
			#evaluate alarm condition
			if (self.zones[zoneID].stateChanged == True):
				if (self.zones[zoneID].status.state.value() == ZONE_STATE_ALARM):
					self.alarmLight.activate(offDelay=None, onDelay=self.settings.alarmDelayLight)
					self.alarmSound.activate(offDelay=None, onDelay=self.settings.alarmDelaySound)
				
				else:
					self.alarmLight.deactivate()
					self.alarmSound.deactivate()

		#panic buttons
		#light
		if (self.inputs.panicAlarmLightTrigger.value() == 1):
			self.inputs.panicAlarmLightTrigger.value(0)
			self.alarmLight.activate(offDelay=None, onDelay=None)

		#sound
		if (self.inputs.panicAlarmSoundTrigger.value() == 1):
			self.inputs.panicAlarmSoundTrigger.value(0)
			self.alarmSound.activate(offDelay=None, onDelay=None)

		#alarm off
		if (self.inputs.alarmOffTrigger.value() == 1):
			self.inputs.alarmOffTrigger.value(0)
			self.alarmSound.deactivate()
			self.alarmLight.deactivate()

		#light alarm handling
		self.alarmLight.update()
		self.outputs.alarmLight.value(self.alarmLight.signalState)
		
		#sound alarm handling
		self.alarmSound.update()
		self.outputs.alarmSound.value(self.alarmSound.signalState)


class alarmCenterInputs:
	"Inputs of alarm centers"
	#init
	def __init__(self, PDI):
		self.panicAlarmLightTrigger = core.modules.iosignal.IOsignal(PDI)
		self.panicAlarmSoundTrigger = core.modules.iosignal.IOsignal(PDI)
		self.alarmOffTrigger = core.modules.iosignal.IOsignal(PDI)


class alarmCenterOutputs:
	"Outputs of alarm centers"
	#init
	def __init__(self, PDI):
		self.alarmLight = core.modules.iosignal.IOsignal(PDI)
		self.alarmSound = core.modules.iosignal.IOsignal(PDI)
		self.armCountDown = core.modules.iosignal.IOsignal(PDI)


class alarmCenterSettings:
	"Settings of  alarm centers"
	#init
	def __init__(self, PDI):
		self.alarmDelayLight = 0
		self.alarmDelaySound = 0
		self.delayToBeArmed = 0
		self.shortFlashTime = 0
		
		
class alarmCenterOperatingModes:
	"Operating modes of alarm centers"
	#init
	def __init__(self, PDI):
		self.switch = core.modules.iosignal.IOsignal(PDI)
		self.types = alarmCenterOperatingModeTypes(PDI)
        
class alarmCenterOperatingModeTypes:
	"Operating modes of alarm centers"
	#init
	def __init__(self, PDI):
		self.automatic = alarmCenterOperatingModeInterface(PDI)
		self.manual = alarmCenterOperatingModeInterface(PDI)

class alarmCenterOperatingModeInterface:
	"Operating modes of alarm centers"
	#init
	def __init__(self, PDI):
		self.armStartTrigger = core.modules.iosignal.IOsignal(PDI)
		self.armEndTrigger = core.modules.iosignal.IOsignal(PDI)
		self.armStartTime = core.modules.iosignal.IOsignal(PDI)
		self.armEndTime = core.modules.iosignal.IOsignal(PDI)
		self.armEnableSwitch = core.modules.iosignal.IOsignal(PDI)

class alarmCenterStatus:
	"Status of alarm centers"
	#init
	def __init__(self, PDI):
		self.state = core.modules.iosignal.IOsignal(PDI)

class alarmCenterZone:
	"Manages zones of alarm centers"
	#init
	def __init__(self, PDI):
		self.inputs = alarmCenterZoneInputs(PDI)
		self.status = alarmCenterZoneStatus(PDI)
		self.alarmCenterState = 0
		self.alarmCenterGlobalAlarmOff = 0
		self.oldState = 0
		self.stateChanged = False
		
	def update(self):
		#keep old state in mind for change driven information
		self.oldState = self.status.state.value()

		#skip zone if deactivated
		if (self.inputs.enable.value() == 0) or (self.alarmCenterState != ALARM_CENTER_STATE_ARMED):
			self.status.state.value(ZONE_STATE_DISABLED)
		elif (self.alarmCenterState == ALARM_CENTER_STATE_ARMED):
			#generate alarm state: as soon as sensor detects something lock alarm state which can only be reseted by off trigger
			if (self.inputs.sensor.value() == 1) or (self.status.state.value() == ZONE_STATE_ALARM):
				self.status.state.value(ZONE_STATE_ALARM)
			else:
				self.status.state.value(ZONE_STATE_NO_ALARM)
			
			if (self.alarmCenterGlobalAlarmOff == 1):
				self.status.state.value(ZONE_STATE_NO_ALARM)


		#generate change flag for one cycle
		if (self.oldState != self.status.state.value()):
			self.stateChanged = True
		else:
			self.stateChanged = False


		
class alarmCenterZoneInputs:
	"Inputs of zones of alarm centers"
	#init
	def __init__(self, PDI):
		self.enable = core.modules.iosignal.IOsignal(PDI)
		self.sensor = core.modules.iosignal.IOsignal(PDI)
		
class alarmCenterZoneStatus:
	"Status of zones of alarm centers"
	#init
	def __init__(self, PDI):
		self.state = core.modules.iosignal.IOsignal(PDI)

class alarmSignalManager:
	"Operates any alarm signal (light, sound, etc.)"
	#init
	def __init__(self):
		self.signalState = 0
		self.samplingTime = 0
		self.lastCallTime = 0
		self.offDelay = None
		self.onDelay = None
		self.onDelayTimer = 0

		
	def activate(self, offDelay=None, onDelay=None):
		self.offDelay = offDelay
		self.onDelay = onDelay

		if (self.onDelay == None):
			self.signalState = 1		#immediate switch on if no onDelay is configured
		else:
			self.onDelayTimer = 0.01	#forces onDelay in update() function
		
	def update(self):
		#cycle time calculation
		self.samplingTime = max(time.time() - self.lastCallTime, 0)
		self.lastCallTime = time.time()
		
		#handle onDelay of alarm signal
		if (self.onDelayTimer > 0) and (self.onDelay != None):
			self.onDelayTimer += self.samplingTime
			if (self.onDelayTimer >= self.onDelay):
				self.signalState = 1
				self.onDelayTimer = 0
		
		#handle offDelay when signal is on and a offDelay is configured
		if (self.offDelay != None) and (self.signalState == 1):
			self.offDelay -= self.samplingTime
			if (self.offDelay <= 0):
				self.signalState = 0
				self.offDelay = None

	def deactivate(self):
		self.signalState = 0
		self.offDelay = None
		self.onDelayTimer = 0


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
        