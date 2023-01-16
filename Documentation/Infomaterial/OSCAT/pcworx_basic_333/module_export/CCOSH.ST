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

this function calculates the arcus tangens function of a complex number
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CCOSH

(*Group:Default*)


VAR_INPUT
	X :	oscat_complex;
END_VAR


VAR_OUTPUT
	CCOSH :	oscat_complex;
END_VAR


(*@KEY@: WORKSHEET
NAME: CCOSH
IEC_LANGUAGE: ST
*)
CCOSH.re := cosH(x.re) * COS(x.im);
CCOSH.im := sinH(x.re) * SIN(x.im);

(* revision history
hm	21. feb 2008	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
