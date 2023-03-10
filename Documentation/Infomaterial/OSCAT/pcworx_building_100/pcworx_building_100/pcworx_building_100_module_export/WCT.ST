(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: HLK
*)
(*@KEY@:DESCRIPTION*)
version 1.2	13. mar. 2009
programmer 	hugo
tested by	tobias

this function calculates the wind chill temperature
(*@KEY@:END_DESCRIPTION*)
FUNCTION WCT:REAL

(*Group:Default*)


VAR_INPUT
	T :	REAL;
	V :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: WCT
IEC_LANGUAGE: ST
*)
IF V < 5.0 OR T > 10.0 THEN
	WCT := T;
ELSE
	WCT := 13.12 + 0.6215 * T +(0.3965 * T - 11.37) * EXP(LN(v) * 0.16);
END_IF;


(* revision history
hm	7 feb 2007		rev 1.0
	original version

hm	7 dec 2007	rev 1.1
	changed code for better performance

hm	13. mar. 2009	rev 1.2
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
