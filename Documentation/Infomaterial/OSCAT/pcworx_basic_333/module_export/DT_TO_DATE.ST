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
FUNCTION DT_TO_DATE:UDINT

(*Group:Default*)


VAR_INPUT
	IN :	UDINT;
END_VAR


(*@KEY@: WORKSHEET
NAME: DT_TO_DATE
IEC_LANGUAGE: ST
*)
(* Zeitanteil aus Date-Time herausfiltern *)
DT_TO_DATE := (IN / UDINT#86400) * UDINT#86400;
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
