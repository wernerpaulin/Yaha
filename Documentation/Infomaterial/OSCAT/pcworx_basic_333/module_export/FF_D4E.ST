(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.FF_EDGE_TRIGGERED
*)
(*@KEY@:DESCRIPTION*)
version 1.3	14. mar. 2009
programmer 	hugo
tested by	oscat

quad D-type flip flop with reset and rising clock trigger

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FF_D4E

(*Group:Default*)


VAR_INPUT
	D0 :	BOOL;
	D1 :	BOOL;
	D2 :	BOOL;
	D3 :	BOOL;
	CLK :	BOOL;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	Q0 :	BOOL;
	Q1 :	BOOL;
	Q2 :	BOOL;
	Q3 :	BOOL;
END_VAR


VAR
	edge :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: FF_D4E
IEC_LANGUAGE: ST
*)
IF rst THEN
	Q0 := FALSE;
	Q1 := FALSE;
	Q2 := FALSE;
	Q3 := FALSE;
ELSIF clk AND NOT edge THEN
	Q0 := D0;
	Q1 := D1;
	Q2 := D2;
	Q3 := D3;
END_IF;
edge := CLK;

(* revision history
hm	4. aug 2006	rev 1.0
	original version

hm	27. dec 2007	rev 1.1
	changed code for better performance

hm	30. oct. 200	rev 1.2
	deleted unnecessary init with 0

hm	14. mar. 2009	rev 1.3
	removed double assignments

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
