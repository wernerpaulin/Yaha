(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_PROCESSING
*)
(*@KEY@:DESCRIPTION*)
version 1.4	10. mar. 2009
programmer 	hugo
tested by	oscat

the function stair2 converts an anlog input signal to a staircase like output.
D is the step width for the output signal. the output will use D as a hysteresis for a stairchange.
if D = 0 then the output follows the input without a chage.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK STAIR2

(*Group:Default*)


VAR_INPUT
	X :	REAL;
	D :	REAL;
END_VAR


VAR_OUTPUT
	Y :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: STAIR2
IEC_LANGUAGE: ST
*)
IF D > 0.0 THEN
	IF X >= Y + D OR X <= Y - D THEN Y := INT_TO_REAL(FLOOR(X/D)) * D; END_IF;
ELSE
	Y := X;
END_IF;


(* revision history
hm	28 jan 2007		rev 1.0
	original version

hm	27. dec 2007	rev 1.1
	changed code for better performance

hm	30. jun. 2008	rev 1.2
	added type conversions to avoid warnings under codesys 3.0																																																												
																																																																											
																																																																											
																																									

ks	26. oct. 2008	rev 1.3
	improved code

hm	10. mar. 2009	rev 1.4
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
