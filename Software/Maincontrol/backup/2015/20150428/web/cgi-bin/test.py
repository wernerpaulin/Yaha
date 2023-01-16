#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json


IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Server_to_Client))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


data = cgi.FieldStorage()
if data['reset'].value == "True":
    counterReset = True
else:
    counterReset = False 

print "Content-type:text/html\r\n"
txData = {"page":"logEnOcean", "reset": counterReset}
print txData

"""    
TXsocket.sendto(json.dumps(txData), (IP_ADR, PORT_Client_to_Server))
rxData, addr = RXsocket.recvfrom(1024) # buffer size is 1024 bytes
#rxData = json.loads(jsonData)

print "Content-type:text/html\r\n"
print rxData
"""

RXsocket.close()
TXsocket.close()
