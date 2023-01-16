(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.AUTOMATION
*)
(*@KEY@:DESCRIPTION*)
version 1.0	28 sep 2007
programmer 	hugo
tested by	tobias

INTERLOCK has two inputs I1 and I2 which drive the corresponding outputs Q1 and Q2.
the inputs signals lock each other out and therfore I1 can only drive Q1 when I2 is Low and vice versa.
The input TL specifies a dead time between two outputs can become active.
an output can only become active when the other output was not active for the time TL.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK INTERLOCK

(*Group:Default*)


VAR_INPUT
	I1 :	BOOL;
	I2 :	BOOL;
	TL :	TIME;
END_VAR


VAR_OUTPUT
	Q1 :	BOOL;
	Q2 :	BOOL;
END_VAR


VAR
	T1 :	TOF;
	T2 :	TOF;
END_VAR


(*@KEY@: WORKSHEET
NAME: INTERLOCK
IEC_LANGUAGE: ST
*)
(* the input signal have a run delay to lockout the other input *)
T1(IN := I1, PT := TL);
T2(IN := I2, PT := TL);

Q1 := I1 AND NOT t2.Q;
Q2 := I2 AND NOT t1.Q;

(* revision history

hm	28 sep 2007		rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
