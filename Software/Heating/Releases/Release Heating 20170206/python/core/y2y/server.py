#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket               # Import socket module
import json
#import core.pdi.yaha_pdi

import fcntl
import struct


IF_NAME_TO_LISTEN = "wlan0"			#eth0 = RJ45 Ethernet plug, wlan0 = wifi adapter

PORT_Client_to_Server = 10010
PORT_Server_to_Client = 10011
RX_TX_BUFFER_SIZE = 8192


class main:
    'Yaha 2 Yaha Communication Server: provides PDI read/write access to other Yaha controllers'

    def __init__(self, PDI):
        self.PDI = PDI
        self.myServerIP = get_ip_address(IF_NAME_TO_LISTEN)  # '10.0.0.90'
        print("Y2Y server IP address: {0}".format(self.myServerIP))
        
        try:
            self.RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.RXsocket.bind((self.myServerIP, PORT_Client_to_Server))
            self.RXsocket.setblocking(False)
            
            self.TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.TXsocket.setblocking(False)
            
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
            self.clientIP = ""
            self.clientPort = 0
            self.tags = 0
            self.restData = ""
        #except Exception as e:          #Python 3
        except Exception, e:		#Python 2
            #In case of an error, reset IP address so server will not be activ
            print("Y2Y server init exception: {0}".format(e))
            self.myServerIP = ""
			

    def update(self):
        #bypass server if init failed
        if (self.myServerIP == ""):
            return
			
        #Receive process data from web bridge - non-blocking call
        if (len(self.txData) == 0):
            try:    #see whether there is data (assume entire frame is there)
                self.jsonDataStream, (self.clientIP, self.clientPort) = self.RXsocket.recvfrom(RX_TX_BUFFER_SIZE)

                try:
                    #convert received data to dictionary and sort read and write requests
                    self.rxData = json.loads(self.jsonDataStream.decode())
                    
                    #print("Y2Y server RX data <{0}> from: {1}".format(self.rxData, self.clientIP))
                    
                    self.tagsToRead.clear()
                    self.tagsToWrite.clear()
                    
                    for self.tag in self.rxData:
                        if (self.rxData[self.tag] == "$read$"):
                            self.tagsToRead[self.tag] = self.rxData[self.tag]
                        else:
                            self.tagsToWrite[self.tag] = self.rxData[self.tag]
                    
                    #update process data image
                    self.tagsToWrite = self.PDI.write(self.tagsToWrite)
                    self.tagsToRead = self.PDI.read(self.tagsToRead)
                    self.txData = merge_dicts(self.tagsToRead, self.tagsToWrite)
                    #print("Y2Y Server TX preparation: " + str(self.txData))
                #except Exception as e: #Python3
                except Exception, e:        #Python 2
                    print("Y2Y Server error <{0}> unpacking json data: {1}".format(e,self.jsonDataStream))
                    self.txData.clear()
            
            #except Exception as e: #try again next cycle in case no date was there. #Python3
            except Exception, e:        #Python 2
                #print("Y2Y Server receive exception: {0}".format(e))
                self.txData.clear()
                
        #prepare reply to other Yaha client
        if (len(self.txData) > 0):
            try:
                #print("Y2Y Server TX send: " + str(self.txData))
                #self.restData = self.TXsocket.sendto(json.dumps(self.txData).encode(encoding='utf_8', errors='strict'), (self.clientIP, PORT_Server_to_Client)) # Python 3: .encode() 
                self.restData = self.TXsocket.sendto(json.dumps(self.txData), (self.clientIP, PORT_Server_to_Client))	#Python 2
                self.txData.clear()
            #except Exception as e: #try again next cycle in case no date was there. #Python3
            except Exception, e:        #Python 2
                print("Y2Y Server send exception: {0}".format(e))
                self.txData.clear()
            

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
        struct.pack('256s', ifname[:15])
    )[20:24])

