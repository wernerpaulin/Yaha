(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.FUNCTIONS
*)
(*@KEY@:DESCRIPTION*)
version 1.5	10. mar. 2009
programmer 	hugo
tested by	oscat

this function calculates the moving average over n samples from a sequential input
the input values are shifted into an N deep buffer and the avg of this buffer is diplayed at anytime on the output.
a rst will load the buffer with the current in value..

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_AVG

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	E :	BOOL := TRUE;
	N :	INT := INT#32;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	AVG :	REAL;
END_VAR


VAR
	buff :	delay;
	i :	INT;
	init :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_AVG
IEC_LANGUAGE: ST
*)
(* limit n to a max of 32 because delay can do max 32 cycles *)
buff.N := LIMIT(0, N, 32);

IF NOT init OR rst THEN
	FOR i := 1 TO N DO
		buff(in := in);
	END_FOR;
	avg := in;
	init := TRUE;
ELSIF E THEN
	buff(in := in);
	avg := avg + (in - buff.out ) / INT_TO_REAL(N);
END_IF;

(* revision history

hm	7. jan. 2007	rev 1.1
	chaged rst logic to load the buffer with the actual input value instead of 0.
	added en input to allow better control of signal flow
	added init to load the buffer with in at startup to avoid rampup at beginning.
	deleted unused variable cnt.

hm	14. jun. 2008	rev 1.2
	set default for input en = TRUE and N = 32

hm	10. oct. 2008	rev 1.3
	improved performance

hm	18. oct. 2008	rev 1.4
	changed input en to e for compatibility reasons

hm	10. mar. 2009	rev 1.5
	added type conversion for compatibility reasons

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
