(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ELECTRICAL
*)
(*@KEY@:DESCRIPTION*)
version 1.0	15. jul. 2008
programmer 	hugo
tested by	oscat

PULSE_T generates a pulse of length T2 if the input pulse is shorter than T1.
if the input pulse is longer than T1, the output follows the input.
and rising edge on in will kill a possible output pulse and generate a new pulse instead.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK PULSE_T

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	T1 :	TIME;
	T2 :	TIME;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
END_VAR


VAR
	init :	BOOL;
	last :	TIME;
	tx :	TIME;
	edge :	BOOL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: PULSE_T
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

IF NOT init THEN
	init := TRUE;
	last := tx;
ELSIF RST THEN
	(* asynchronous reset *)
	Q := FALSE;
ELSIF IN AND NOT edge AND NOT Q THEN
	(* a rising edge on in will reversre the output status, if new pulse is startet the start time is stored in last *)
	last := tx;
	Q := TRUE;
ELSIF NOT IN AND edge AND ((tx - last) > T1) THEN
	(* a falling edge on IN will clear the output if in was high for more then T1 *)
	Q := FALSE;
ELSIF (tx - last) >= T2 THEN
	(* timeout for long pulse if second click did not occur or in stays high *)
	Q := FALSE;
END_IF;

edge := IN;

(* revision histroy
hm	15. jul. 2008	rev 1.0
	original release


*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
