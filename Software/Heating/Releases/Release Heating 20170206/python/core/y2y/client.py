#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

import socket               # Import socket module
import json
#import core.pdi.yaha_pdi

import fcntl
import struct
import threading
import time

PORT_Client_to_Server = 10010
PORT_Server_to_Client = 10011
RX_TX_BUFFER_SIZE = 8192

IO_SIMULATION_ACTIVE_PDI_TAG = "ioSimulation"

Y2Y_TIMEOUT = 4



class main():
    "Specific IO handler for Yaha 2 Yaha communication"
    def __init__(self, PDI):
        #IF_NAME:wlan0.SERVER-IP:0A:00:00:5C.IN.serverProcessTag:ioActTempLivingroom.interval:5.invalidValue:0.defaultValue:23
        self.IF_NAME_INDEX = 0
        self.SERVER_IP_INDEX = 1
        self.DIRECTION_INDEX = 2
        self.SERVER_PROCESS_TAG_INDEX = 3
        self.INTERVAL_INDEX = 4                #optional
        self.INVALID_VALUE_INDEX = 5        #optional
        self.DEFAULT_VALUE_INDEX = 6        #optional
        
        self.PDI = PDI
        
        self.ioTags = dict()
        self.idStringElements = list() 
        self.readTags = dict()
        self.writeTags = dict()
        
        self.clientList = dict()    #"IP-Adr" : class 

        #get all PDI tags where Y2Y is specified as owner => all these tags will be handled by the Y2Y client
        self.ioTags = PDI.getTagDeviceIDs('Y2Y')  #"tag" : ID
        
        for tag in self.ioTags:
            try:
                #device IDs are formated like: IF_NAME:wlan0.SERVER-IP:0A:00:00:5C.IN.serverProcessTag:ioActTempLivingroom.interval:5.invalidValue:0.defaultValue:23
                self.idStringElements = self.ioTags[tag].split(".")
                
                #convert client IP address from hex to decimal string
                myInterfaceName = self.idStringElements[self.IF_NAME_INDEX].split(":")[1].lower()
                serverIPhex = self.idStringElements[self.SERVER_IP_INDEX].lower()
                serverIPint = "{0}.{1}.{2}.{3}".format( int(serverIPhex[10:12],16), 
                                                        int(serverIPhex[13:15],16), 
                                                        int(serverIPhex[16:18],16), 
                                                        int(serverIPhex[19:21],16) )
                #create an client infrastructure for each server which should be accessed if it does not yet exists
                if (serverIPint not in self.clientList):
                    self.clientList[serverIPint] = y2yClient(myInterfaceName, serverIPint, PORT_Server_to_Client, PORT_Client_to_Server, self.PDI)
                
                #add this IO point data to client list and fill in io configuration data
                self.clientList[serverIPint].ioList[tag] = ioPoint()
                self.clientList[serverIPint].ioList[tag].direction = self.idStringElements[self.DIRECTION_INDEX].lower()
                self.clientList[serverIPint].ioList[tag].serverProcessTag = self.idStringElements[self.SERVER_PROCESS_TAG_INDEX].split(":")[1]
                self.clientList[serverIPint].ioList[tag].interval = self.idStringElements[self.INTERVAL_INDEX].split(":")[1]
                self.clientList[serverIPint].ioList[tag].invalidValue = self.idStringElements[self.INVALID_VALUE_INDEX].split(":")[1]
                self.clientList[serverIPint].ioList[tag].defaultValue = self.idStringElements[self.DEFAULT_VALUE_INDEX].split(":")[1]
        
            except Exception as e:
                print("IO: error in PDI owner ID for Y2Y: {0}".format(e))            
            
        #start driver only if PDI tags are configured for GPIO
        if (len(self.ioTags) > 0):
            self.start()

    def start(self):
        #abort start if simulation is active
        try:
            if (getattr(self.PDI, IO_SIMULATION_ACTIVE_PDI_TAG) == 1):
                print("WARNING: Y2Y IO simulation is active")
                return
        except:
            pass

        for clients in self.clientList:
            self.clientList[clients].connect()

        
    def readInputs(self):
        #abort read if simulation is active
        try:
            if (getattr(self.PDI, IO_SIMULATION_ACTIVE_PDI_TAG) == 1):
                return
        except:
            pass

        #go through all tags which should be read from io driver and write current value directly into PDI
        for clients in self.clientList:
            self.clientList[clients].readInputs()


    def writeOutputs(self):
        #abort read if simulation is active
        try:
            if (getattr(self.PDI, IO_SIMULATION_ACTIVE_PDI_TAG) == 1):
                return
        except:
            pass

        #go through all write tags and see if it has been changed since last write
        for clients in self.clientList:
            self.clientList[clients].writeOutputs()

            
class y2yClient():
    "Client handler to server IP address"    
    def __init__(self, myInterfaceName, serverIP, rxPortNr, txPortNr, PDI):
        self.serverIP = serverIP
        self.clientIP = ""
        self.myInterfaceName = myInterfaceName
        self.rxPortNr = rxPortNr
        self.txPortNr = txPortNr
        self.ioList = dict()
        self.connectError = False

        self.serverRequestThreadID = 0
        self.jsonDataStream = ""
        self.senderIP = None
        self.senderPort = None


    def connect(self):
        self.clientIP = get_ip_address(self.myInterfaceName)
        print("Y2Y client IP address: {0}".format(self.clientIP))
        
        try:
            self.RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.RXsocket.bind((self.clientIP, self.rxPortNr))
            self.RXsocket.setblocking(True)        #blocking because we wait in a parallel thread for a reply from server
            self.RXsocket.settimeout(Y2Y_TIMEOUT/2)          #timeout 50% of thread timeout
            
            self.TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.TXsocket.setblocking(False)        #blocking because we wait in a parallel thread for a reply from server
            
            self.txData = {'empty': 0}          #force creating a dictionary
            self.txData.clear()                 #clear dictionary immediately
            self.tagsToRead = {'empty': 0}      #force creating a dictionary
            self.tagsToRead.clear()             #clear dictionary immediately
            self.tagsToWrite = {'empty': 0}     #force creating a dictionary
            self.tagsToWrite.clear()            #clear dictionary immediately
            self.txData = {'empty': 0}          #force creating a dictionary
            self.txData.clear()                 #clear dictionary immediately
            self.rxData = {'empty': 0}          #force creating a dictionary
            self.rxData.clear()                 #clear dictionary immediately
            
            self.jsonDataStream = ""
            self.restData = ""
            self.connectError = False

        except Exception as e:          #Python 3
            #In case of an error, reset IP address so client will not be activ
            print("Y2Y client init exception: {0}".format(e))
            self.clientIP = ""
            self.connectError = True
    
        
    def serverRequestThread(self):
        """
        Burner update disablen
        Datenpunkt testweise in XML configurieren -> dann im Excel"
        
        4. Read und Write mergen alle read/write Anfragen
        4a. Schreiben mit count1 testen
        5. Client auf Python 3 umbauen
        wieder aktivieren: print("Y2Y (IP: {0}): not finished in one cycle
        """

        #update process data image
        try:
            #{"count1":"$read$"}
            #{"count1”:0}

            #self.tagsToWrite["ioActTempLivingroom"] = "$read$"
            self.tagsToWrite["count1"] = "$read$"
            self.txData = merge_dicts(self.tagsToRead, self.tagsToWrite)

            self.jsonDataStream = json.dumps(self.txData) # Python 3: .encode() 

            self.TXsocket.sendto(self.jsonDataStream.encode(encoding='utf_8', errors='strict'), (self.serverIP, self.txPortNr)) 
            print("Y2Y TX frame {0} to {1} at port {2}".format(self.jsonDataStream, self.serverIP, self.txPortNr))
        except Exception as e:          #Python 3
            print("Y2Y TX socket exception: {0}".format(e))
        
        try:
            self.jsonDataStream, (self.senderIP, self.senderPort) = self.RXsocket.recvfrom(RX_TX_BUFFER_SIZE)
            if (self.senderIP == self.serverIP):
                print("Y2Y frame {0} received from {1} at port {2}".format(self.jsonDataStream, self.senderIP, self.senderPort))
            else:
                print("Y2Y unexpected frame received: sender IP:<{0}>, expected from IP: <{1}>".format(self.senderIP, self.serverIP))
        except Exception as e:          #Python 3
            print("Y2Y RX socket exception: {0}".format(e))

        
    def readInputs(self):
        return
        if (self.connectError == True):
            return

        try:
            #check if communication has been finished while main cycle has sleeping
            if (self.serverRequestThreadID.isAlive() == False):
                #copy latest received (triggered during write cycle) values to PDI
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!WEITER MACHEN"
            
            elif ( (time.time() - self.requestStartTime) >= Y2Y_TIMEOUT ):
                print("Server (IP: {0}): timeout".format(self.serverIP))
                
                try:
                    #close and reopen again
                    RXsocket.close()
                    TXsocket.close()  
                    self.connectError = True
                    self.connect()
                except:
                    pass
            else:
                pass
                #print("Y2Y (IP: {0}): not finished in one cycle. Elapsed time: {1}".format(self.serverIP, (time.time() - self.requestStartTime)))
        except:
            #thread has not been started (could happen after boot up when write happens after the first cycle)
            pass



        
    def writeOutputs(self):
        return
        if (self.connectError == True):
            return

        #before starting another communication thread, check whether the old one has been terminated (= thread function finished)
        try:
            if (self.serverRequestThreadID.isAlive() == True):
                return
        except:
            #thread handle invalid = thread not yet started => also ok. Continue with starting a new thread
            pass
        
        #entire Y2Y read/write communication happens here: write is called at the end of the cycle time which gives enough time for communication until the new cycle starts (read data are then already available)
        try:
            #start synchronous modbus read/write as thread to not block cyclic system
            self.serverRequestThreadID = threading.Thread(target=self.serverRequestThread)
            self.requestStartTime = time.time()
            self.serverRequestThreadID.start()
            return
        
        except Exception as e:
            print("Y2Y (Server IP: {0}): starting thread failed: {1}".format(self.serverIP, e))
            return  




    
class ioPoint():
    "Representation of a single IO point"    
    def __init__(self):
        self.direction = None
        self.serverProcessTag = None
        self.interval = None
        self.invalidValue = None         #if this value is received it is considered as invalid and the default value will be used (e.g. Enocean temperature not yet received)
        self.defaultValue = None         #the PDI tag will be set to this value in case an invalid value has been received
        

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    call: z = merge_dicts(a, b, c, d, e, f, g) where a-g are dictionaries (can be extended unlimited: h,i,j,...)
    
    dict1 = {"key1": 10, "key2": 20, "key3": 30}
    dict2 = {"key3": 40, "key5": 50, "key6": 60}

    print(merge_dicts(dict1,dict2))
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))            #python 3: convert ifname to bytes before!
    )[20:24])  


      
