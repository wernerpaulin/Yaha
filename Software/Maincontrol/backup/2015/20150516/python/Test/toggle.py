#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime, threading, time
import RPi.GPIO as GPIO ## Import GPIO Library
import time ## Import 'time' library.  Allows us to use 'sleep'

GPIO.setmode(GPIO.BOARD) ## Use BOARD pin numbering
GPIO.setup(11, GPIO.OUT) ## Setup GPIO pin 11 to OUT

global toggleState


def foo():
    next_call = time.time()
    toggleState = False

    while True:
        print (datetime.datetime.now())
        
        if toggleState == False:
            GPIO.output(11, GPIO.HIGH)
            toggleState = True
        else:
            GPIO.output(11, GPIO.LOW)
            toggleState = False
        
        next_call = next_call+0.1;
        time.sleep(next_call - time.time())

timerThread = threading.Thread(target=foo)
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