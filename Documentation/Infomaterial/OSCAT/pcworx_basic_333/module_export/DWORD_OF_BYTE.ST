(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GATE_LOGIC
*)
(*@KEY@:DESCRIPTION*)
version 1.3	18. jul. 2009
programmer 	hugo
tested by	tobias

this function creates a Dword from 4 individual bytes
(*@KEY@:END_DESCRIPTION*)
FUNCTION DWORD_OF_BYTE:DWORD

(*Group:Default*)


VAR_INPUT
	B3 :	BYTE;
	B2 :	BYTE;
	B1 :	BYTE;
	B0 :	BYTE;
END_VAR


(*@KEY@: WORKSHEET
NAME: DWORD_OF_BYTE
IEC_LANGUAGE: ST
*)
DWORD_OF_BYTE := SHL(SHL(SHL(BYTE_TO_DWORD(B3),8) OR BYTE_TO_DWORD(B2),8) OR BYTE_TO_DWORD(B1),8) OR BYTE_TO_DWORD(B0);

(* revision history
hm	24. jan 2007	rev 1.0
	original version

hm 2. jan 2008	rev 1.1
	inproved performance

hm	23. apr. 2008	rev 1.2
	reverse order of inputs to be more logical

hm	18. jul. 2009	rev 1.3
	added type conversions for compatibility reasons
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
