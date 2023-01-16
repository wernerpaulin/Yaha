(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.AUTOMATION
*)
(*@KEY@:DESCRIPTION*)
version 1.0	23. mar. 2009
programmer 	hugo
tested by	tobias

driver_4C is a multi purpose driver.
a rising edge on in switches from S0 state S1 and the next edge to state S2 and so on.
in state S0 all outputs Q are FALSE.
The stet of the Outputs in any state S? is configurable with setup variables.
The variables S1..S5 define the states, while the sequence is terminated when a state Variable S? = 0.
The lower bits 0..3 of the state vars S? are corresponding to the Outputs Q0..Q3

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK DRIVER_4C

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	RST :	BOOL;
	TIMEOUT :	TIME;
	SX :	oscat_DRIVER_4C;
END_VAR


VAR_OUTPUT
	SN :	INT;
	Q0 :	BOOL;
	Q1 :	BOOL;
	Q2 :	BOOL;
	Q3 :	BOOL;
END_VAR


VAR
	off :	TON;
	edge :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: DRIVER_4C
IEC_LANGUAGE: ST
*)
IF RST OR off.Q THEN
	SN := 0;
ELSIF IN AND NOT edge THEN
	SN := SN + 1;
	IF SN > 7 OR SX[SN] = BYTE#0 THEN SN := 0; END_IF;
END_IF;
edge := in;
IF SN > 0 THEN
	Q0 := (SX[SN] AND BYTE#1) > BYTE#0;
	Q1 := (SX[SN] AND BYTE#2) > BYTE#0;
	Q2 := (SX[SN] AND BYTE#4) > BYTE#0;
	Q3 := (SX[SN] AND BYTE#8) > BYTE#0;
ELSE
	Q0 := FALSE;
	Q1 := FALSE;
	Q2 := FALSE;
	Q3 := FALSE;
END_IF;

(* maximaum timeout *)
IF timeout > t#0s THEN off(in := SN > 0, PT := Timeout); END_IF;


(* revision history
hm	23. mar. 2009	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
