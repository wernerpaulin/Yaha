============================================================
Summary
============================================================

Pymodbus is a full Modbus protocol implementation using twisted for its
asynchronous communications core. It can also be used without any third
party dependencies (aside from pyserial) if a more lightweight project is
needed.

============================================================
Features
============================================================

------------------------------------------------------------
Client Features
------------------------------------------------------------

  * Full read/write protocol on discrete and register
  * Most of the extended protocol (diagnostic/file/pipe/setting/information)
  * TCP, UDP, Serial ASCII, Serial RTU, and Serial Binary
  * asynchronous(powered by twisted) and synchronous versions
  * Payload builder/decoder utilities

------------------------------------------------------------
Server Features
------------------------------------------------------------

  * Can function as a fully implemented modbus server
  * TCP, UDP, Serial ASCII, Serial RTU, and Serial Binary
  * asynchronous(powered by twisted) and synchronous versions
  * Full server control context (device information, counters, etc)
  * A number of backing contexts (database, redis, a slave device)

============================================================
Use Cases
============================================================

Although most system administrators will find little need for a Modbus
server on any modern hardware, they may find the need to query devices on
their network for status (PDU, PDR, UPS, etc).  Since the library is written
in python, it allows for easy scripting and/or integration into their existing
solutions.

Continuing, most monitoring software needs to be stress tested against
hundreds or even thousands of devices (why this was originally written), but
getting access to that many is unwieldy at best. The pymodbus3 server will allow
a user to test as many devices as their base operating system will allow (*allow*
in this case means how many Virtual IP addresses are allowed).

For more information please browse the project documentation:
http://readthedocs.org/docs/pymodbus3/en/latest/index.html

------------------------------------------------------------
Example Code
------------------------------------------------------------

For those of you that just want to get started fast, here you go::

    from pymodbus3.client.sync import ModbusTcpClient
    
    client = ModbusTcpClient('127.0.0.1')
    client.write_coil(1, True)
    result = client.read_coils(1,1)
    print result.bits[0]
    client.close()

For more advanced examples, check out the examples included in the
repository. If you have created any utilities that meet a specific
need, feel free to submit them so others can benefit.

Also, if you have questions, please ask them on the mailing list
so that others can benefit from the results and so that I can
trace them. Also you can write to issue tracker:
https://github.com/uzumaxy/pymodbus3/issues

------------------------------------------------------------
Installing
------------------------------------------------------------

You can install using pip or easy install by issuing the following
commands in a terminal window (make sure you have correct
permissions or a virtualenv currently running)::

    easy_install -U pymodbus3
    pip install -U pymodbus3

Otherwise you can pull the trunk source and install from there::

    git clone https://github.com/uzumaxy/pymodbus3.git
    cd pymodbus3
    python setup.py install

Either method will install all the required dependencies
(at their appropriate versions) for your current python distribution.

If you would like to install pymodbus3 without the twisted dependency,
simply edit the setup.py file before running easy_install and comment
out all mentions of twisted.  It should be noted that without twisted,
one will only be able to run the synchronized version as the
asynchronous versions uses twisted for its event loop.

------------------------------------------------------------
Current Work In Progress
------------------------------------------------------------

Listing of immediate tasks:

  * Fixing bugs/feature requests
  * Architecture documentation
  * Functional testing against any reference I can find
  * The remaining edges of the protocol (that I think no one uses)
   
------------------------------------------------------------
License Information
------------------------------------------------------------

Pymodbus is built on top of code developed from/by:
  * Copyright (c) 2001-2005 S.W.A.C. GmbH, Germany.
  * Copyright (c) 2001-2005 S.W.A.C. Bohemia s.r.o., Czech Republic.
  * Hynek Petrak <hynek@swac.cz>
  * Twisted Matrix

Released under the BSD License
