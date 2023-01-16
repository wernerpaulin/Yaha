(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 1.0	16. jul. 2008
programmer 	hugo
tested by	oscat

this Module decodes a specified number of clicks.
the output trig is high for one cycle if N clicks are present within a specified time TC.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CLICK_CNT

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	N :	INT;
	TC :	TIME;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
END_VAR


VAR
	tx :	TP;
	edge :	BOOL;
	cnt :	INT := INT#-1;
END_VAR


(*@KEY@: WORKSHEET
NAME: CLICK_CNT
IEC_LANGUAGE: ST
*)
(* Q shall only be active for one cycle only *)
Q := FALSE;

IF in AND NOT edge AND NOT tx.q THEN
	(* a rising edge on in sets the counter to 0 *)
	cnt := 0;
ELSIF tx.Q AND NOT IN AND edge THEN
	(* count falling edges when tp.q is true *)
	cnt := cnt + 1;
ELSIF NOT tx.Q THEN
	Q := cnt=N;
	cnt := -1;
END_IF;

(* remember the status of IN *)
edge := IN;
tx(in := IN, pt := TC);

(* revision history

hm 	16. jul. 2008	rev 1.0
	original version released


*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
