(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.FUNCTIONS
*)
(*@KEY@:DESCRIPTION*)
version 1.4	25 jan 2008
programmer 	oscat
tested BY	oscat

this ramp function follows an input signal with a linear ramp up or down, the up or down speed can be set with KF and KR.
a K factor of 1 means 1 unit per second on the output. K factors can only be positive and not negative.
a busy output signals the ramp is running or busy false means the in value is present on the output.
a rmp input false means the output follows the input dierctly while a rmp = true means the output follows the input with a ramp.
a updn output signal the directon of the ramp (up or down).
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_RMP

(*Group:Default*)


VAR_INPUT
	RMP :	BOOL := TRUE;
	IN :	REAL;
	KR :	REAL;
	KF :	REAL;
END_VAR


VAR_OUTPUT
	OUT :	REAL;
	BUSY :	BOOL;
	UD :	BOOL;
END_VAR


VAR
	tx :	TIME;
	last :	TIME;
	init :	BOOL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_RMP
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS) - last;

IF NOT init THEN
	init := TRUE;
	last := tx;
	tx := t#0s;
	out := in;
END_IF;
IF NOT rmp THEN
	out := in;
	busy := FALSE;
ELSIF out > in THEN
	(* ramp down *)
	out := out - TIME_TO_REAL(tx) * 0.001 * KF;
	out := MAX(in, out);
ELSIF out < in THEN
	(* ramp up *)
	out := out + TIME_TO_REAL(tx) * 0.001 * KR;
	out := MIN(in, out);
END_IF;

(* set busy and dir flags *)
IF out < in THEN
	busy := TRUE;
	ud := TRUE;
ELSIF out > in THEN
	busy := TRUE;
	ud := FALSE;
ELSE
	busy := FALSE;
END_IF;
last := last + tx;


(* revision history:

hm 8.10.2006			rev 1.1
	added ud output

hm 12. feb 2007		rev 1.2
	added init variable and corrected a possible startup problem

hm	17. sep 2007	rev 1.3
	replaced time() with t_plc_ms() for compatibility reasons

hm	25. jan 2008	rev 1.4
	performance improvements
	allow KR and KF to be 0
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
