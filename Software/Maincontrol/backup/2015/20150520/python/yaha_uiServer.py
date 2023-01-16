#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_uiServer.py &

import yaha_pdi
import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json
import py_utilities

yaha_pdi.YahaPDIcreate('/home/pi/Yaha/pdi/yaha_pdi.xml')
#yaha_pdi.YahaPDIcreate('C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python/yaha_pdi.xml')


processData = {'empty': 0}    #force creating a dictionary
processData.clear()           #clear dictionary immediately



def foo():
    global toggleCount

    next_call = time.time()
    toggleCount = 0

    while True:
        toggleCount = toggleCount + 1
        #print (datetime.datetime.now())
        #print (toggleCount)
        
        next_call = next_call+0.1
        time.sleep(next_call - time.time())

timerThread = threading.Thread(target=foo)
timerThread.start()



IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
RX_TX_BUFFER_SIZE = 4096
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Client_to_Server))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

txData = {'empty': 0}    #force creating a dictionary
txData.clear()           #clear dictionary immediately
tagsToRead = {'empty': 0}    #force creating a dictionary
tagsToRead.clear()           #clear dictionary immediately
tagsToWrite = {'empty': 0}    #force creating a dictionary
tagsToWrite.clear()           #clear dictionary immediately

while True:    
    jsonDataStream, addr = RXsocket.recvfrom(RX_TX_BUFFER_SIZE)
 
    processData['count1'] = toggleCount
    yaha_pdi.YahaPDIwriteValue(processData, {})
    
    #convert received data to dictionary and sort read and write requests
    rxData = json.loads(jsonDataStream)
    tagsToRead.clear()
    tagsToWrite.clear()
    
    for tag in rxData:
        if (rxData[tag] == "$read$"):
            tagsToRead[tag] = rxData[tag]
        else:
            tagsToWrite[tag] = rxData[tag]
            
    tagsToWrite = yaha_pdi.YahaPDIwriteValue({}, tagsToWrite)
    tagsToRead = yaha_pdi.YahaPDIreadValue({}, tagsToRead)

    #merge both return dictionary to one big one for reply
    txData = py_utilities.merge_dicts(tagsToRead, tagsToWrite)
    print(txData)
    TXsocket.sendto(json.dumps(txData), (IP_ADR, PORT_Server_to_Client))


RXsocket.close()
TXsocket.close()
