#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket               # Import socket module
import json
import py_utilities
import yaha_data

IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
RX_TX_BUFFER_SIZE = 4096


class Server:
    'Yaha User Interface Server: communicates with CGI python script of web server'

    def __init__(self):
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
                self.rxData = json.loads(self.jsonDataStream)
                self.tagsToRead.clear()
                self.tagsToWrite.clear()

                for self.tag in self.rxData:
                    if (self.rxData[self.tag] == "$read$"):
                        self.tagsToRead[self.tag] = self.rxData[self.tag]
                    else:
                        self.tagsToWrite[self.tag] = self.rxData[self.tag]
                
                #update process data image
                self.tagsToWrite = yaha_data.YahaPDIwriteValue({}, self.tagsToWrite)
                self.tagsToRead = yaha_data.YahaPDIreadValue({}, self.tagsToRead)
                self.txData = py_utilities.merge_dicts(self.tagsToRead, self.tagsToWrite)

            except: #try again next cycle in case no date was there.
                self.txData.clear()
        
        #prepare reply to web bridge
        if (len(self.txData) > 0):
            print(self.txData)
            self.restData = self.TXsocket.sendto(json.dumps(self.txData), (IP_ADR, PORT_Server_to_Client))
            self.txData.clear()
       
