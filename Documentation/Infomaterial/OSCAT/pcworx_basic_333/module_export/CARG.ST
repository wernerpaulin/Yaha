(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.COMPLEX
*)
(*@KEY@:DESCRIPTION*)
version 1.1	20. apr. 2008
programmer 	hugo
tested by	oscat

this function calculates the phase angle (argument) of a complex number
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CARG

(*Group:Default*)


VAR_INPUT
	X :	oscat_complex;
END_VAR


VAR_OUTPUT
	CARG :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: CARG
IEC_LANGUAGE: ST
*)
CARG := ATAN2(X.im, X.re);

(* revision history
hm	21. feb. 2008	rev 1.0
	original version

hm	20. apr. 2008	rev 1.1
	use ATAN2 instead of ATAN
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
