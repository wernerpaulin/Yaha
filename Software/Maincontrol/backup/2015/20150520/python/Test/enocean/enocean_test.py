#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
sys.path.append("/home/pi/Yaha/enocean")
sys.path.append("/home/pi/Yaha/enocean/communicators")
sys.path.append("/home/pi/Yaha/enocean/protocol")

#addtional packages:
#sudo apt-get install python3-bs4
sys.path.append("/home/pi/Yaha/enum34-1.0.4/")


from enocean.consolelogger import init_logging
from enocean.communicators.serialcommunicator import SerialCommunicator
from enocean.protocol.packet import Packet
from enocean.protocol.constants import PACKET, RORG
import sys
import traceback

try:
    import queue
except ImportError:
    import Queue as queue

p = Packet(PACKET.COMMON_COMMAND, [0x08])

init_logging()
c = SerialCommunicator()
c.start()
c.send(p)
while c.is_alive():
    try:
        # Loop to empty the queue...
        p = c.receive.get(block=True, timeout=1)
        if p.type == PACKET.RADIO and p.rorg == RORG.BS4:
            for k in p.parse_eep(0x02, 0x05):
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.BS1:
            for k in p.parse_eep(0x00, 0x01):
                print('%s: %s' % (k, p.parsed[k]))
        if p.type == PACKET.RADIO and p.rorg == RORG.RPS:
            for k in p.parse_eep(0x02, 0x04):
                print('%s: %s' % (k, p.parsed[k]))
    except queue.Empty:
        continue
    except KeyboardInterrupt:
        break
    except Exception:
        traceback.print_exc(file=sys.stdout)
        break

if c.is_alive():
    c.stop()

