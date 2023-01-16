#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/core/y2y/send_test.py

import socket

UDP_IP = "8.8.8.8"
UDP_PORT = 10010
MESSAGE = "Hello, World!"

 
print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

sock.close()