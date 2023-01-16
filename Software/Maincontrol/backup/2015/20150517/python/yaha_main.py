#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, threading, time

def SystemTick():
    next_call = time.time()

    while True:
        print (datetime.datetime.now())
        
        next_call = next_call+0.1
        time.sleep(next_call - time.time())

timerThread = threading.Thread(target=SystemTick)
timerThread.start()


# compensate time() call, adjust sleep according to runtime of function, watchdog
"""
#Zugriff auf Process Data Image
import threading

L = threading.Lock()

L.acquire()
# The critical section ...
L.release()
"""