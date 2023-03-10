 
[hardwarekonfig]
wurzel: 2
[2.1]
spi: OBJEKTID=3
{2.3}
klasse: "HC_Moduluebersicht.Class"
name: _PRJ-Moduluebersicht
[1.1]
[1.100]
modulname: CPU
version: 1.0.0.0
anschlussgrp: "eth1"
anschlussinfo: NUMMER=1, MODULID=4, FLAGS=1
[1.101]
[1.1632]
comparam_eth1: IP=192.168.0.1, MASK=255.255.0.0, GATEWAY=0.0.0.0, BROADCAST=255.255.255.255, FORCE
inaparam_eth1: NODENO=2, PORTNO=11159, FORCE
cfgparam_eth1: SOCKETCNT=16, DESCRCNT=16, MEMBUFCNT=453, ARPTBLENTRCNT=16, PAGECNT=16, ROUTINGENTRCNT=0, FBSERVERPORT=11159, FBTCPPRI=182, PNADAEMONPRI=184, LIBPRI=183, BROADCASTCNT=5
[1.1824]
{1.108}
klasse: "ModbusCPU"
[5.1]
[5.100]
moduladr: 0
verbunden: 4
station: 1
busart: 6
version: 1.0.1.0
[5.101]
[5.1824]
{5.1856}
klasse: "X20PS9400a"
comparam: 
[12.1]
[12.100]
moduladr: 0
verbunden: 4
station: 6
busart: 6
version: 1.1.2.0
[12.101]
[12.1824]
{12.1856}
klasse: "X20DO2633"
comparam: 
[13.1]
[13.100]
moduladr: 0
verbunden: 4
station: 7
busart: 6
version: 1.1.2.0
[13.101]
[13.1824]
{13.1856}
klasse: "X20DO2633"
comparam: 
[14.1]
[14.100]
moduladr: 0
verbunden: 4
station: 8
busart: 6
version: 1.1.2.0
[14.101]
[14.1824]
{14.1856}
klasse: "X20DO2633"
comparam: 
[4.1]
[4.100]
verbunden: 1
knotennr: 1
station: 1
busart: 8
version: 1.1.0.0
anschlussgrp: "x2x1"
anschlussinfo: NUMMER=1, MODULID=5, FLAGS=1
anschlussinfo: NUMMER=2, MODULID=6, FLAGS=1
anschlussinfo: NUMMER=3, MODULID=7, FLAGS=1
anschlussinfo: NUMMER=4, MODULID=8, FLAGS=1
anschlussinfo: NUMMER=5, MODULID=9, FLAGS=1
anschlussinfo: NUMMER=6, MODULID=12, FLAGS=1
anschlussinfo: NUMMER=7, MODULID=13, FLAGS=1
anschlussinfo: NUMMER=8, MODULID=14, FLAGS=1
anschlussinfo: NUMMER=9, MODULID=15, FLAGS=1
[4.101]
[4.1648]
comparam: MASK=0.0.0.255, GATEWAY=0.0.0.0, DHCP
[4.1840]
comparam_x2x1: SYNCUSAGE=50, IOSIZE=8, RESPTIME=100, BUSLENGTH=1000, STATIONS=64, ASYNCPAYLOAD=80
timingparam_x2x1: CYCLETIME=1000, PRESCALE=1
{4.1824}
klasse: "X20BC0087"
[15.1]
[15.100]
moduladr: 0
verbunden: 4
station: 9
busart: 6
version: 1.1.2.0
[15.101]
[15.1824]
{15.1856}
klasse: "X20DO2633"
comparam: 
[3.1]
spi: OBJEKTID=1
spi: OBJEKTID=4
spi: OBJEKTID=5
spi: OBJEKTID=6
spi: OBJEKTID=7
spi: OBJEKTID=8
spi: OBJEKTID=9
spi: OBJEKTID=12
spi: OBJEKTID=13
spi: OBJEKTID=14
spi: OBJEKTID=15
{3.2}
klasse: "HC_SPS.Class"
familie: 111
modulname: modbus_bc
[6.1]
[6.100]
moduladr: 0
verbunden: 4
station: 2
busart: 6
version: 1.2.0.0
[6.101]
[6.1824]
{6.1856}
klasse: "X20AT4222"
comparam: 
[7.1]
[7.100]
moduladr: 0
verbunden: 4
station: 3
busart: 6
version: 1.2.0.0
[7.101]
[7.1824]
{7.1856}
klasse: "X20AT4222"
comparam: 
[8.1]
[8.100]
moduladr: 0
verbunden: 4
station: 4
busart: 6
version: 1.0.2.0
[8.101]
[8.1824]
{8.1856}
klasse: "X20DI4653"
comparam: 
[9.1]
[9.100]
moduladr: 0
verbunden: 4
station: 5
busart: 6
version: 1.0.2.0
[9.101]
[9.1824]
{9.1856}
klasse: "X20DO2649"
comparam: 
