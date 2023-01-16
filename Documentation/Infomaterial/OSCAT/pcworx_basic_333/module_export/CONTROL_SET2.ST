(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 1.1	11. mar. 2009
programmer 	hugo
tested by	tobias

takahashi calculates controller parameters for P, PI and PID controllers based on the ziegler nichols method.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CONTROL_SET2

(*Group:Default*)


VAR_INPUT
	KS :	REAL;
	TU :	REAL;
	TG :	REAL;
	PI :	BOOL;
	PID :	BOOL;
	P_K :	REAL := 1.0;
	PI_K :	REAL := 0.9;
	PI_TN :	REAL := 3.33;
	PID_K :	REAL := 1.2;
	PID_TN :	REAL := 2.0;
	PID_TV :	REAL := 0.5;
END_VAR


VAR_OUTPUT
	KP :	REAL;
	TN :	REAL;
	TV :	REAL;
	KI :	REAL;
	KD :	REAL;
END_VAR


VAR
	TX :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: CONTROL_SET2
IEC_LANGUAGE: ST
*)
IF TU > 0.0 AND KS > 0.0 THEN TX := TG / TU / KS; END_IF;
IF pi AND PID THEN
	KP := 0.0;
	TN := 0.0;
	TV := 0.0;
ELSIF PID THEN
	KP := PID_K * TX;
	TN := PID_TN * TU;
	TV := PID_TV * TU;
ELSIF PI THEN
	KP := PI_K * TX;
	TN := PI_TN * TU;
ELSE
	KP := P_K * TX;
END_IF;

(* KI and KD are calculated *)
IF TN > 0.0 THEN KI := KP / TN; ELSE KI := 0.0; END_IF;
KD := KP * TV;

(* revision history
hm	4. nov 2007	rev 1.0
	original version

hm	11. mar. 2009	rev 1.1
	real constants updated to new systax using dot																																																															
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																																											
																																																								

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
