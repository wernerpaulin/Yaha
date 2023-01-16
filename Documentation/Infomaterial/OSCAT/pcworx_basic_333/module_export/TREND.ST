(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_PROCESSING
*)
(*@KEY@:DESCRIPTION*)
version 1.0	21. aug. 2009
programmer 	hugo
tested by	oscat

trend analyses the trend of a input signal.
The Output Q is True if the input X is >= last_X and is false if the input X is <= last_X
in addition to the trend the output TU will be high for one cycle to signal a rising of the input value X
and  TD will signal a decreasing value on the input X.
in case of a change the output D will show the delta of the input to the last input value.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK TREND

(*Group:Default*)


VAR_INPUT
	X :	REAL;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	TU :	BOOL;
	TD :	BOOL;
	D :	REAL;
END_VAR


VAR
	last_x :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: TREND
IEC_LANGUAGE: ST
*)
TU := X > last_X;
TD := X < last_X;
Q := TU OR TD;
D := X - LAST_X;

last_X := X;



(* revision history
hm	21. aug. 2009	rev 1.0
	original version

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
