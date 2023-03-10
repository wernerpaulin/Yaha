(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.COMPLEX
*)
(*@KEY@:DESCRIPTION*)
version 1.0	21 feb 2008
programmer 	hugo
tested by	oscat

this function calculates the sinus function of a complex number
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CSIN

(*Group:Default*)


VAR_INPUT
	X :	oscat_complex;
END_VAR


VAR_OUTPUT
	CSIN :	oscat_complex;
END_VAR


(*@KEY@: WORKSHEET
NAME: CSIN
IEC_LANGUAGE: ST
*)
CSIN.re := cosH(X.im) * SIN(X.re);
CSIN.im := sinH(X.im) * COS(X.re);

(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
