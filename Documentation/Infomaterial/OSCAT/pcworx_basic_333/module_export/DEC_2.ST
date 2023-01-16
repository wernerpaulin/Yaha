(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GATE_LOGIC
*)
(*@KEY@:DESCRIPTION*)
version 1.1	3 Mar 2007
programmer 	hugo
tested by	tobias

a bit input will be decoded to the two outputs Q0 or Q1
dependent on the value of A
A=0 decodes to Q0 and A=1 decodes to Q1
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK DEC_2

(*Group:Default*)


VAR_INPUT
	D :	BOOL;
	A :	BOOL;
END_VAR


VAR_OUTPUT
	Q0 :	BOOL;
	Q1 :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: DEC_2
IEC_LANGUAGE: ST
*)
Q0 := D AND NOT A;
Q1 := D AND A;

(* revision history
hm 3.3.2007	rev 1.1
	rewritten in ST for better compatibility
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
