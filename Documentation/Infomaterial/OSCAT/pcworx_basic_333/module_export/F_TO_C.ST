(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONVERSION
*)
(*@KEY@:DESCRIPTION*)
version 1.1	11. mar. 2009
programmer 	hugo
tested BY	tobias

this FUNCTION converts fahrenheit TO celsius

(*@KEY@:END_DESCRIPTION*)
FUNCTION F_TO_C:REAL

(*Group:Default*)


VAR_INPUT
	FAHRENHEIT :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: F_TO_C
IEC_LANGUAGE: ST
*)
F_TO_C := (fahrenheit - 32.0) * 0.5555555555555;

(* revision history
hm	4. aug 2006	rev 1.0
	original version

hm	11. mar. 2009	rev 1.1
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
