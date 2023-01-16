#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket               # Import socket module
import json
import core.pdi.yaha_pdi

IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
RX_TX_BUFFER_SIZE = 4096


class Server:
    'Yaha User Interface Server: communicates with CGI python script of web server'

    def __init__(self, PDI):
        self.PDI = PDI
        self.RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.RXsocket.bind((IP_ADR, PORT_Client_to_Server))
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
        self.addr = 0
        self.tags = 0
        self.restData = 0

    def update(self):
        #Receive process data from web bridge - non-blocking call
        if (len(self.txData) == 0):
            try:    #see whether there is data (assume entire frame is there)
                self.jsonDataStream, self.addr = self.RXsocket.recvfrom(RX_TX_BUFFER_SIZE)

                #convert received data to dictionary and sort read and write requests
                self.rxData = json.loads(self.jsonDataStream.decode())
                
                #print("UI RX: " + str(self.rxData))
                
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
                #print("UI TX: " + str(self.txData))
            except Exception as e: #try again next cycle in case no date was there.
                #print("UI Update exception: {0}".format(e))
                self.txData.clear()
        
        #prepare reply to web bridge
        if (len(self.txData) > 0):
            #print("TX: " + str(self.txData))
            self.restData = self.TXsocket.sendto(json.dumps(self.txData).encode(encoding='utf_8', errors='strict'), (IP_ADR, PORT_Server_to_Client)) # python 3: .encode()
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
