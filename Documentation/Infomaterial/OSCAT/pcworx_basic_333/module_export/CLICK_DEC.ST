(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 1.1	14. mar. 2009
programmer 	hugo
tested by	oscat

this Module detects a rising edge on In and decodes the amount of falling edges (Pulses) within a specified time TC.
the outputs Q0..Q3 will go true for one cycle and the amount of clicks within a specified time TC.
if only a rising egde is detected within TC Q0 will respond, Q1 for 1 pulse and so on..

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CLICK_DEC

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	TC :	TIME;
END_VAR


VAR_OUTPUT
	Q0 :	BOOL;
	Q1 :	BOOL;
	Q2 :	BOOL;
	Q3 :	BOOL;
END_VAR


VAR
	tx :	TP;
	edge :	BOOL;
	cnt :	INT := INT#-1;
END_VAR


(*@KEY@: WORKSHEET
NAME: CLICK_DEC
IEC_LANGUAGE: ST
*)
(* Q shall only be active for one cycle only *)
IF in = FALSE THEN
	Q0 := FALSE;
	Q1 := FALSE;
	Q2 := FALSE;
	Q3 := FALSE;
END_IF;

IF in AND NOT edge AND NOT tx.q THEN
	(* a rising edge on in sets the counter to 0 *)
	cnt := 0;
ELSIF tx.Q AND NOT IN AND edge THEN
	(* count falling edges when tp.q is true *)
	cnt := cnt + 1;
ELSIF NOT tx.Q THEN
	CASE cnt OF
		0 : Q0 := TRUE;
		1 : Q1 := TRUE;
		2 : Q2 := TRUE;
		3 : Q3 := TRUE;
	END_CASE;
	cnt := -1;
END_IF;

(* remember the status of IN *)
edge := IN;
tx(in := IN, pt := TC);



(* revision history

hm 17. jul. 2008	rev 1.0
	original version released

hm	14. mar. 2009	rev 1.1
	removed double assignments

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
