(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.ARRAY_FUNCTIONS
*)
(*@KEY@:DESCRIPTION*)
version 1.1	10. mar. 2009
programmer 	hugo
tested by	tobias

this function will calculate the geometric average of a given array.


(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK ARRAY_GAV

(*Group:Default*)


VAR_IN_OUT
	PT :	oscat_pt_ARRAY;
END_VAR


VAR_INPUT
	SIZE :	UINT;
END_VAR


VAR_OUTPUT
	ARRAY_GAV :	REAL;
END_VAR


VAR
	i :	INT;
	stop :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: ARRAY_GAV
IEC_LANGUAGE: ST
*)
stop :=LIMIT_INT(1,UINT_TO_INT(size),1000);
ARRAY_GAV := 1.0;
FOR i := 1 TO stop DO
	IF pt[i] > 0.0 THEN
		ARRAY_GAV := ARRAY_GAV * pt[i];
	ELSE
		ARRAY_GAV := 0.0;
		RETURN;
	END_IF;
END_FOR;
ARRAY_GAV := SQRTN(ARRAY_GAV,stop);

(* revision history
hm	2. apr 2008	rev 1.0
	original version

hm	10. mar. 2009	rev 1.1
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
