(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.MEASUREMENTS
*)
(*@KEY@:DESCRIPTION*)
version 2.5	18. mar. 2011
programmer 	oscat
tested by	tobias

ONTIME measures the ontime of a signal in seconds.
the output SECONDS is of type DWORD which results in a total measurement range of 1 second up to 136 years.
internally ontime works with a resolution of milliseconds
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK ONTIME

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	RST :	BOOL;
END_VAR


VAR_IN_OUT
	SECONDS :	UDINT;
	CYCLES :	UDINT;
END_VAR


VAR
	tx :	UDINT;
	last :	UDINT;
	edge :	BOOL;
	init :	BOOL;
	ms :	UDINT;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: ONTIME
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= T_PLC_MS.T_PLC_MS;

(* make sure the first cycle works correctly *)
IF NOT init THEN
	init := TRUE;
	last := tx;
	ms := UDINT#0;
END_IF;
IF RST THEN
	SECONDS := UDINT#0;
	CYCLES := UDINT#0;
	last := tx;
	ms := UDINT#0;
ELSIF IN THEN
	(* add the current milliseconds *)
	ms := (tx - last) + ms;
	IF ms >= UDINT#1000 THEN
		seconds := seconds + UDINT#1;
		ms := ms - UDINT#1000;
	END_IF;
	cycles := cycles + BOOL_TO_UDINT(NOT edge);
END_IF;
last := tx;
edge := in;


(* revision history
hm 22.2.2007		rev 1.1
	changed VAR RETAIN PERSISTENT to VAR RETAIN for better compatibility
	wago lon contollers do not support persisitent

hm 2.8.2007		rev 1.2
	adding time up in a real number will automatically lead to the point where 
	small time scales like the cycle time will be below the resolution of real and therefore
	ontime would not increase in small steps as necessary
	the time is now measured internally in two  dwords and be converted to real only for
	output purposes.
	deleted the variable power because it was unnecessary

hm	16.9.2007		rev 1.3
	changes time() to T_plc_ms() for compatibility reasons

hm	2. dec. 2007	rev 1.4
	chaged code for better performance

hm	16. mar. 2008	rev 1.5
	added type conversions to avoid warnings under codesys 3.0

hm	21. oct. 2008	rev 2.0
	changed module for much better performance and allow for external result storage

hm	10. nov. 2008	rev 2.1
	increased internal resolution to milliseconds

hm	16. nov. 2008	rev 2.2
	changed typecast to avoid warnings

hm	17. dec. 2008	rev 2.3
	fixed an error when in would be true for more then 49 days

hm	17. jan 2011	rev 2.4
	init will not clear seconds and cycles, only rst clears these values	

hm	18. mar. 2011	rev 2.5
	reset was not working

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
