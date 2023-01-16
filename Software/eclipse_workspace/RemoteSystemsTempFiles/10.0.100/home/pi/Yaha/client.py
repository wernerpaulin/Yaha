#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json
import sys
  

IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.bind((IP_ADR, PORT_Server_to_Client))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) > 1:
    if sys.argv[1] == "1":
        txData = {"page":"logEnOcean", "reset": True}
    else:
        txData = {"page":"logEnOcean", "reset": False}
else:
    txData = {"page":"logEnOcean", "reset": False}
    
TXsocket.sendto(json.dumps(txData), (IP_ADR, PORT_Client_to_Server))
data, addr = RXsocket.recvfrom(1024) # buffer size is 1024 bytes
print "client: received message:", data

