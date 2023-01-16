(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GATE_LOGIC
*)
(*@KEY@:DESCRIPTION*)
version 1.2	16. oct. 2008
programmer 	hugo
tested BY	oscat

dual input multiplexer
depending on the value of A0, D0 or D1 will be switched to the Output
(*@KEY@:END_DESCRIPTION*)
FUNCTION MUX_2:BOOL

(*Group:Default*)


VAR_INPUT
	D0 :	BOOL;
	D1 :	BOOL;
	A0 :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: MUX_2
IEC_LANGUAGE: ST
*)
MUX_2 := SEL(A0, D0, D1);


(*
revision history:
hm	5.10.2006		rev 1.1
	changed to ST Langage for better portability.

hm	16. oct. 2008	rev 1.2
	improved performance

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
