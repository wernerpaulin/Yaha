(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: EMULATION
*)
(*@KEY@:DESCRIPTION*)

(*@KEY@:END_DESCRIPTION*)
FUNCTION REAL_TO_TIME:TIME

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: REAL_TO_TIME
IEC_LANGUAGE: ST
*)
REAL_TO_TIME := DINT_TO_TIME(UDINT_TO_DINT(_REAL_TO_UDINT(IN)));
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
