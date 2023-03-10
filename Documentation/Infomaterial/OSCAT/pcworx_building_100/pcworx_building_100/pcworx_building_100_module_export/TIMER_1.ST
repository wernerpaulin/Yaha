(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ELECTRICAL
*)
(*@KEY@:DESCRIPTION*)
version 2.2	16. dec. 2009
programmer 	oscat
tested by	oscat

this is a simple timer that generates an output pulse on selected days.
the output pulse width can be programmed with duration, if set to 0 no pulse is generated.
day specifies the specific days for the event to occur, bit 0 = sunday, bit 1 = saturday, bit 2 = friday ....
for all days to be active 127 has to be specified for DAY.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK TIMER_1

(*Group:Default*)


VAR_INPUT
	E :	BOOL := TRUE;
	DTI :	UDINT;
	START :	UDINT;
	DURATION :	TIME;
	DAY :	BYTE := BYTE#2#0111_1111;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	STOP :	TIME;
END_VAR


(*@KEY@: WORKSHEET
NAME: TIMER_1
IEC_LANGUAGE: ST
*)
IF E THEN
	stop := TOD_TO_TIME(START) + DURATION;
	IF stop > T#24h THEN stop := stop - T#24h; END_IF;
	Q := TIMECHECK(DT_TO_TOD(DTI), START, TIME_TO_TOD(stop)) AND (SHR(BYTE#128, DAY_OF_WEEK(DT_TO_DATE(DTI))) AND DAY) > BYTE#0;
ELSE
	Q := FALSE; (* clear output when e is not true *)
END_IF;

(*
1.12.2006 hm		rev 1.1
	corrected an error with pulse width = 0.

25.12.2006 hm		rev 1.2
	corrected an error when timer overflows.

14.apr 2007 hm		rev 1.3
	corrected an error while while output would not go active when start year would be 1970.
	increase accuracy by checking every 100ms
	added init section to compensate for timer overflow

15.9.2007 hm		rev 1.4
	replaced Time() with T_PLC_MS for compatibility and performance reasons

hm	1. okt 2007		rev 1.5
	corrected an error while output would not stay active over midnight.

hm	17. jan 2008	rev 1.6
	New code with better performance  
	Output is now only active during the time of day it is supposed to 
	no pulse is generated at power up

hm	7. oct. 2008	rev 1.7
	changed function weekday to day_of_week

hm	23. oct. 2008	rev 2.0
	new code, added input E, now days can be selected by bits in byte day

hm	6. nov. 2008	rev 2.1
	added default for input EN and input DAY

hm 16. dec 2009	rev 2.2
	fixed a bug over midnight

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
