#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json


def foo():
    global toggleCount

    next_call = time.time()
    toggleCount = 0

    while True:
        #print (datetime.datetime.now())
        
        toggleCount = toggleCount + 1
        #print (toggleCount)
        
        next_call = next_call+0.1
        time.sleep(next_call - time.time())

timerThread = threading.Thread(target=foo)
timerThread.start()



IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Client_to_Server))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:    
    data, addr = RXsocket.recvfrom(1024) # buffer size is 1024 bytes
    rxData = json.loads(data)
    if rxData['reset'] == True:
        toggleCount = 0
    
    TXsocket.sendto(str(toggleCount), (IP_ADR, PORT_Server_to_Client))

        