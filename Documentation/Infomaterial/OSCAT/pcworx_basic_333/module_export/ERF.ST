(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.MATHE
*)
(*@KEY@:DESCRIPTION*)
version 1.3	10. mar. 2009
programmer 	hugo
tested by	tobias

this function calculates the erf (error) function.

(*@KEY@:END_DESCRIPTION*)
FUNCTION ERF:REAL

(*Group:Default*)


VAR_INPUT
	X :	REAL;
END_VAR


VAR
	x2 :	REAL;
	ax2 :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: ERF
IEC_LANGUAGE: ST
*)
x2 := X*X;
ax2 := 0.147 * x2 + 1.0;
ERF := SQRT(1.0 - EXP(-X2 * ((0.27323954473516 + aX2)/(ax2)))) * INT_TO_REAL(SGN(x));




(* revision history
hm	7. apr. 2008	rev 1.0
	original version

hm	30. jun. 2008	rev 1.1
	added type conversions to avoid warnings under codesys 3.0

hm	25. oct. 2008	rev 1.2
	new code using new algorithm

hm	10. mar. 2009	rev 1.3
	real constants updated to new systax using dot
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
