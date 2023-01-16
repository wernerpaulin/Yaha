(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 2.0	23. oct. 2008
programmer 	oscat
tested BY	oscat

this ramp generator generates a Word wide ramp with 65535 steps
the generator has an asynchronous set and reset
the ramp is controlled by PT which is the total ramp time for a full sweep from 0..65535
an UD input controlls the direction Up or Down and the E input enables the ramp generation
a busy output indicates that the ramp is running, busy false means output is stable.
the outputs low and high will be true when the output has reached its max or min value.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK RMP_W

(*Group:Default*)


VAR_INPUT
	SET :	BOOL;
	PT :	TIME;
	E :	BOOL := TRUE;
	UP :	BOOL := TRUE;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	OUT :	WORD;
	BUSY :	BOOL;
	HIGH :	BOOL;
	LOW :	BOOL;
END_VAR


VAR
	rmp :	_RMP_W;
END_VAR


(*@KEY@: WORKSHEET
NAME: RMP_W
IEC_LANGUAGE: ST
*)
(* generate ramp *)
rmp(dir := UP, E := E, TR := PT, rmp := out);
out := rmp.RMP;

(* set or reset operation *)
IF RST THEN
	out := WORD#0;
ELSIF SET THEN
	out := WORD#65535;
END_IF;

(* checks for outputs stable and reset or set busy flag *)
low := out = WORD#0;
high := out = WORD#65535;
busy := NOT (low OR high) AND E;


(* revision history:

hm 4.10.2006		rev 1.1
	added the busy output which signals that the ramp is running.

hm 22.1.2007		rev 1.2
	deleted unused variable step

hm	17.9.2007		rev 1.3
	replaced time() with t_plc_ms() for compatibility reasons

hm	28. sep 2007	rev 1.4
	added outputs on and off
	busy is now disabled while en is false
	new coding for higher accuracy and performance

hm	5. oct 2007	rev 1.5
	added statements to allow for PT to be t#0s output jumps to max or min immediately

hm	2. dec 2007	rev 1.6
	corrected an error in calculation of step response

hm	25. dec 2007	rev 1.7
	corrected an error while step response was too slow for fast rise times

hm	16. oct. 2008	rev 1.8
	improved performance

hm	18. oct. 2008	rev 1.9
	renamed inout EN to E for compatibility reasons

hm	23. oct. 2008	rev 2.0
	new code using _RMP_W
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
