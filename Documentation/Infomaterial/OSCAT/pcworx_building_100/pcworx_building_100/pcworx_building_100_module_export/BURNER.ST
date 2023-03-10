(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: HLK
*)
(*@KEY@:DESCRIPTION*)
version 1.5	15 sep 2007
programmer 	oscat
tested by	oscat

burner ist eine Oel-Brenner_steuerung fuer nichtmodulierende Oelbrenner
die steuerung kann ueber setup werte programmiert werden und entsprechenden brennern angepasst werden.
die vorheizzeit ist die zeit die eine oelvorwaermung aufgeheizt wird bevor der motor gestartet wird.
der eingang oil_temp gibt an ob die oil_temp erreicht wurde, er ist default auf true und kann auch offen gelassen werden.
die vorbelueftungszeit ist die zeit die der luefter laeuft bevor die oelzufuhr freigegeben wird.
die vorzuendzeit iust diejenige zeit die die zuendung vor offnen des oelventiel gestartet wird.
nachzuendzeit ist die zeit die nach entzuendung der flamme noch gezuendet wird.
die sicherheitszeit ist die zeit nach der die oelzufuhr gesperrt wird wenn keine flamme entsteht.
nach ablauf der sicherheitszeit wird ein fehler flag gesetzt und kann erst nach der sperrzeit wieder durch einen reset geloescht werden.
waehrend der sperrzeit ist keine weitere zuendung oder einschalten moeglich.
das flag mehrfachzuendung gibt an ob eine erloschene flamme in betrieb automatisch wieder gezuendet werden soll.
der flammwaechster liegt auf eingang flamme, ein uebertemperaturschutz auf dem eingang over_temp
der betriebsstundenzaehler gibt die brennerstunden in stunden als real ausgabewer an.
der ausgang motor steuert den luefter / pumpenmotor, oil_ventil schaltet das oil ventil und zuendung schaltet die zuendung ein.

if output fail > 0 an error happened and the output has an error code:
0 :	no error
1 :	pre heating time expired and oil temp input is not true
2 :	flame monitor is active during preheating time
3 :	flame monitor active during pre_ventilation_time
4 :	no ignoition during safety time
5 :	no flame during operation
9 :	overtemp input is true
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK BURNER

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	STAGE2 :	BOOL;
	OVER_TEMP :	BOOL;
	OIL_TEMP :	BOOL := TRUE;
	FLAME :	BOOL;
	RST :	BOOL;
	RST_TIMER :	BOOL;
	PRE_HEAT_TIME :	TIME := t#5s;
	PRE_VENT_TIME :	TIME := t#15s;
	PRE_IGNITE_TIME :	TIME := t#5s;
	POST_IGNITE_TIME :	TIME := t#25s;
	STAGE2_DELAY :	TIME := t#10s;
	SAFETY_TIME :	TIME := t#5s;
	LOCKOUT_TIME :	TIME := t#10s;
	MULTIPLE_IGNITION :	BOOL := TRUE;
	KW1 :	REAL;
	KW2 :	REAL;
END_VAR


VAR_OUTPUT
	MOTOR :	BOOL;
	COIL1 :	BOOL;
	COIL2 :	BOOL;
	PRE_HEAT :	BOOL;
	IGNITE :	BOOL;
	KWH :	REAL;
	STATUS :	BYTE;
	FAIL :	BOOL;
END_VAR


VAR_IN_OUT
	RUNTIME1 :	UDINT;
	RUNTIME2 :	UDINT;
	CYCLES :	UDINT;
END_VAR


VAR
	state :	INT;
	last :	TIME;
	tx :	TIME;
	last_change :	TIME;
	timer1 :	ONTIME;
	timer2 :	ONTIME;
	oil_temp_last :	BOOL;
	cycles2 :	UDINT;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: BURNER
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* check rst input and overtemp *)
IF rst OR over_temp OR state = 0 THEN
	IF status > BYTE#0 AND tx - last_change >= lockout_time AND rst THEN
		status := BYTE#110;
		fail := FALSE;
		state := 1;
	ELSE
		(* normaler reset *)
		motor := FALSE;
		coil1 := FALSE;
		coil2 := FALSE;
		ignite := FALSE;
		pre_heat := FALSE;
		IF over_temp THEN
			status := BYTE#9;
			fail := TRUE;
		END_IF;
		last_change := tx;
		last := tx;
		state := 1;
	END_IF;
END_IF;

(* check for timer rst and rst timer if true *)
IF rst_timer THEN
	runtime1 := UDINT#0;
	runtime2 := UDINT#0;
	cycles := UDINT#0;
	cycles2 := UDINT#0;
END_IF;

(* quit here if an error is present *)
IF (status > BYTE#0 AND status < BYTE#100) OR rst THEN RETURN; END_IF;

(* start sequence *)
CASE state OF

1:	(* in signal starts oil pre heating *)
	IF in AND flame THEN
		state := 7;
		pre_heat := FALSE;
		status := BYTE#2;
		last_change := tx;
	ELSIF in THEN
		pre_heat := TRUE;
		state := 2;
		last_change := tx;
	END_IF;

2:	(* after pre_heating time start motor *)
	IF (tx- last_change >= pre_heat_time AND oil_temp) OR (oil_temp AND NOT oil_temp_last) THEN
		motor := TRUE;
		state := 3;
		last_change := tx;
	(* pre_heat_time ist abgelaufen und oil_temp ist nicht aktiv *)
	ELSIF tx - last_change >= pre_heat_time AND NOT oil_temp THEN
		state := 7;
		pre_heat := FALSE;
		status := BYTE#1;
		last_change := tx;
	(* flame monitor cannot be active at this time *)
	ELSIF flame THEN
		state := 7;
		pre_heat := FALSE;
		status := BYTE#2;
		last_change := tx;
	END_IF;

3:	(* abwarten bis z?ndung eingeschaltet werden kann *)
	IF tx - last_change >= pre_vent_time - pre_ignite_time THEN
		ignite := TRUE;
		state := 4;
		last_change := tx;
	(* flame monitor cannot be active at this time *)
	ELSIF flame THEN
		state := 7;
		pre_heat := FALSE;
		motor := FALSE;
		status := BYTE#3;
		last_change := tx;
	END_IF;

4:	(* warten bis oelzufuhr geoeffnet werden darf *)
	IF tx - last_change >= pre_ignite_time THEN
		coil1 := TRUE;
		state := 5;
		last_change := tx;
	END_IF;

5:	(* warten auf flammwaechter und falls noetig abschalten *)
	IF tx - last_change >= safety_time OR flame THEN
		IF NOT flame THEN
			(* notabschaltung da flammwaechster nicht angesprochen hat *)
			state := 7;
			motor := FALSE;
			coil1 := FALSE;
			pre_heat := FALSE;
			ignite := FALSE;
			status := BYTE#4;
			last_change := tx;
		ELSE
			state := 6;
			last_change := tx;
		END_IF;
	END_IF;

6:	(* brenner l?uft, flammueberwachung und nach ablauf der nachigniteszeit ignite abschalten *)
	IF NOT flame AND NOT multiple_ignition THEN
		(* notabschaltung da flammwaechster keine flamme meldet *)
		state := 7;
		motor := FALSE;
		coil1 := FALSE;
		coil2 := FALSE;
		pre_heat := FALSE;
		ignite := FALSE;
		status := BYTE#5;
		last_change := tx;
	ELSIF NOT flame AND multiple_ignition THEN
		ignite := TRUE;
		state := 5;
		coil2 := FALSE;
		last_change := tx;
	ELSE
		IF tx - last_change >= post_ignite_time THEN
			(* post_ignite_time abgelaufen, ignite abschalten *)
			ignite := FALSE;
		END_IF;
		IF tx - last_change >= stage2_delay AND stage2 THEN
			coil2 := TRUE;
		ELSE
			coil2 := FALSE;
		END_IF;
	END_IF;
END_CASE;

(* abschaltung wenn kein eingangssignal *)
IF NOT in THEN
	state := 1;
	motor := FALSE;
	coil1 := FALSE;
	coil2 := FALSE;
	ignite := FALSE;
	pre_heat := FALSE;
	last_change := tx;
END_IF;

(* runtimez?hler *)
timer1(in := flame AND in AND motor AND coil1 AND NOT coil2, SECONDS := runtime1, CYCLES := cycles);
cycles := timer1.CYCLES;
runtime1 := timer1.SECONDS;

timer2(in := flame AND in AND motor AND coil1 AND coil2, SECONDS := runtime2, CYCLES := cycles2);
cycles2 := timer2.CYCLES;
runtime2 := timer2.SECONDS;

KWH := UDINT_TO_REAL(runtime1) * KW1 / 3600.0 + UDINT_TO_REAL(runtime2) * KW2 / 3600.0;

(* zeit fuer naechsten aufruf merken *)
last := tx;

(* set fail output IF ERROR and Status  if normal operation *)

IF status > BYTE#0 AND status < BYTE#100 THEN
	fail := TRUE;
ELSE
	fail := FALSE;
	IF NOT in THEN
		status := BYTE#110;
	ELSIF flame AND in AND motor AND coil2 AND coil1 THEN
		status := BYTE#113;
	ELSIF flame AND in AND motor AND coil1 THEN
		status := BYTE#112;
	ELSE
		status := BYTE#111;
	END_IF;
END_IF;


(*
31.12.2006	hm		rev 1.1
	added pre_heat timing and output
	flame monitor before ignition will generate error on status output
	added output for KWh

31.12.2006	hm		rev 1.2
	added oil_temp_input

31.12.2006	hm		rev 1.3
	changed status output to be byte instead of bool

22.1.2007		hm		rev 1.4
	renamed fail output to status
	added output cycles
	corrected an error while pre_heat would be on when an error was present
	added coil2 output and stage2 input

15.9.2007		hm		rev 1.5
	replaced Time() with T_PLC_MS for compatibility and performance reasons

hm	21. oct. 2008	rev 1.6
	changed code to use new ontime rev 2.0	
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
