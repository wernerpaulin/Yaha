(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.GEOMETRY
*)
(*@KEY@:DESCRIPTION*)
version 1.2	10. mar. 2009
programmer 	hugo
tested by	oscat

ellipse_C calculates the circumference of an ellipe based on the two radians R1 and R2

(*@KEY@:END_DESCRIPTION*)
FUNCTION ELLIPSE_C:REAL

(*Group:Default*)


VAR_INPUT
	R1 :	REAL;
	R2 :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: ELLIPSE_C
IEC_LANGUAGE: ST
*)
ELLIPSE_C := 3.14159265358979323846264338327950288 * (3.0 * (R1+R2) - SQRT((3.0 * r1 + R2) * (3.0 * r2 + r1)));

(* revision histroy
hm	16. oct 2007	rev 1.0
	original version

hm	18. oct. 2008	rev 1.1
	using math constants

hm	10. mar. 2009	rev 1.2
	changed syntax of real constants to 0.0

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
