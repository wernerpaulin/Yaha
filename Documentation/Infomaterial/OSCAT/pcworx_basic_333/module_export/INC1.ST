(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.MATHE
*)
(*@KEY@:DESCRIPTION*)
version 1.2	23. feb. 2009
programmer 	hugo
tested by	oscat

This is a increment function which increments the variable X by 1 and if N is reached, it begins with 0 instead of N again.
inc1(X,3) will generate 0,1,2,0,1,.....
(*@KEY@:END_DESCRIPTION*)
FUNCTION INC1:INT

(*Group:Default*)


VAR_INPUT
	X :	INT;
	N :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: INC1
IEC_LANGUAGE: ST
*)
IF X >= N - 1 THEN
	INC1 := 0;
ELSE
	INC1 := X + 1;
END_IF;

(* this elegant version is 50% slower
INC1 := X := (x + 1) MOD N;
*)

(* revision history
hm	13. oct. 2008	rev 1.0
	original version

hm	22. oct. 2008	rev 1.1
	added statement to return value for compatibility reasons

hm	23. feb. 2009	rev 1.2
 	when inc1 is called with X >= N inc will continue with 0
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
