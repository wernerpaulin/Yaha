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
tested by	tobias

triangle_A calculates the Area of a triangle.
if any input is 0 it will be neglected and the are will be calculated from eiter:
two sides and an angle (s1 and S2 and the angle A1) or 3 sides.


(*@KEY@:END_DESCRIPTION*)
FUNCTION TRIANGLE_A:REAL

(*Group:Default*)


VAR_INPUT
	S1 :	REAL;
	A :	REAL;
	S2 :	REAL;
	S3 :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: TRIANGLE_A
IEC_LANGUAGE: ST
*)
IF A = 0.0 THEN
	TRIANGLE_A := SQRT((s1+s2+S3) * (s1+s2-S3) * (S2+S3-S1) * (S3+S1-S2)) * 0.25;
ELSE
	TRIANGLE_A := S1 * S2 * SIN(RAD(A)) * 0.5;
END_IF;

(* revision histroy
hm	16. oct 2007	rev 1.0
	original version

hm	22. feb 2008	rev 1.1
	improved performance

hm	10. mar. 2009	rev 1.2
	changed syntax of real constants to 0.0

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
