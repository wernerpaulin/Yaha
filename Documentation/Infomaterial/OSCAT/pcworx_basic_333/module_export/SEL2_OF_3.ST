(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_PROCESSING
*)
(*@KEY@:DESCRIPTION*)
version 1.1	10. mar. 2009
programmer 	oscat
tested BY	oscat

SEL2_OF_3 checks if 3 input Signals are within a distance D from each other and calculates the average of the 3 inputs do not offset more than D from each other.
If 1 input is more than D greater or smaller than any other input it will be ignored and the average will be calcualted from the remaining 2 Inputs.
In the case the Output is only calculated from 2 Inputs a Warning Output W will display the Number of the discarded Input. if none of the 3 Inputs are within the allowed Delata D from each other, 
an Error Output E is set True and the last valid Output will remain active until at least 2 Inputs are within a valid Range from each other.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK SEL2_OF_3

(*Group:Default*)


VAR_INPUT
	IN1 :	REAL;
	IN2 :	REAL;
	IN3 :	REAL;
	D :	REAL;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	W :	INT;
	E :	BOOL;
END_VAR


VAR
	D12 :	BOOL;
	D23 :	BOOL;
	D31 :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SEL2_OF_3
IEC_LANGUAGE: ST
*)
D12 := ABS(IN1-IN2) <= D;
D23 := ABS(IN2-IN3) <= D;
D31 := ABS(IN3-IN1) <= D;

IF (D12 AND D23) OR (D12 AND D31) OR (D23 AND D31) THEN
	(* all 3 inputs are valid *)
	Y := (IN1 + IN2 + IN3) * 0.333333333333;
	E := FALSE;
	W := 0;
ELSIF D12 THEN
	(* only inut 1 and 2 are valid *)
	Y := (In1 + IN2) * 0.5;
	E := FALSE;
	W := 3;
ELSIF D23 THEN
	(* only inut 2 and 3 are valid *)
	Y := (In2 + IN3) * 0.5;
	E := FALSE;
	W := 1;
ELSIF D31 THEN
	(* only inut 3 and 1 are valid *)
	Y := (In3 + IN1) * 0.5;
	E := FALSE;
	W := 2;
ELSE
	(* no calculation possible *)
	E := TRUE;
	W := 4;
END_IF;


(* revision history
hm	18. may 2008	rev 1.0
	original version

hm	10. mar. 2009	rev 1.1
	improved code
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
