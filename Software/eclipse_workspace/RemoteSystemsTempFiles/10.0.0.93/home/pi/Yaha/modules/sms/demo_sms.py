#!/usr/bin/env python
#python3 /home/pi/Yaha/modules/sms/demo_sms.py

"""\
Demo: handle incoming SMS messages by replying to them

Simple demo app that listens for incoming SMS messages, displays the sender's number
and the messages, then replies to the SMS by saying "thank you"
"""

from __future__ import print_function

import logging

PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
PIN = "0733" # SIM card PIN (if any)

from gsmmodem.modem import GsmModem

def handleSms(sms):
    print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    print('Replying to SMS...')
    sms.reply(u'SMS received: "{0}{1}"'.format(sms.text[:20], '...' if len(sms.text) > 20 else ''))
    print('SMS sent.\n')
    
def main():
    print('Initializing modem...')
    # Uncomment the following line to see what the modem is doing:
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.smsTextMode = True 
    modem.connect(PIN)
    #modem.sendSms("+4366488653519", "Alarm central power up", waitForDeliveryReport=True)

    print('Waiting for SMS message...')    
    try:    
        #modem.rxThread.join(2**31) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
        modem.rxThread.join()
    finally:
        modem.close();

if __name__ == '__main__':
    main()
