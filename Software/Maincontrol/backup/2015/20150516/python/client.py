#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/client.py

import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json
import sys
  

IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
RX_TX_BUFFER_SIZE = 4096
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.bind((IP_ADR, PORT_Server_to_Client))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) > 1:
    if sys.argv[1] == "1":
        txData = {'uiCount1': 0, "uiVar1": 10, "uiVar2": 20, "uiVar3": 30}
    else:
        txData = {"uiCount1":"$read$", "uiVar1": "$read$", "uiVar2": "$read$", "uiVar3": "$read$"}
else:
    txData = {"uiCount1":"$read$", "uiVar1": "$read$", "uiVar2": "$read$", "uiVar3": "$read$"}
    
TXsocket.sendto(json.dumps(txData), (IP_ADR, PORT_Client_to_Server))
data, addr = RXsocket.recvfrom(RX_TX_BUFFER_SIZE) 
print "client: received message:", data

RXsocket.close()
TXsocket.close()