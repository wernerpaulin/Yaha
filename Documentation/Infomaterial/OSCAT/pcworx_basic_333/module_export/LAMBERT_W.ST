(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.MATHE
*)
(*@KEY@:DESCRIPTION*)
version 1.1	10. mar. 2009
programmer 	hugo
tested by	oscat

this function calculates the lambert_w function.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK LAMBERT_W

(*Group:Default*)


VAR_INPUT
	X :	REAL;
END_VAR


VAR_OUTPUT
	LAMBERT_W :	REAL;
END_VAR


VAR
	w :	REAL;
	i :	INT;
	we :	REAL;
	w1e :	REAL;
	last :	DWORD;
	ewx :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: LAMBERT_W
IEC_LANGUAGE: ST
*)
(* check for valid input and return -1000 if too low *)
IF x < -0.367879441171442 THEN
	LAMBERT_W := -1000.0;
	RETURN;
(* return 0 if x = 0 *)
ELSIF x = 0.0 THEN
	RETURN;
(* first an estimate is calculated *)
ELSIF x <= 500.0 THEN
	w := LN(x + 1.0);
	w := 0.665 * (1.0 + 0.0195 * w) * w + 0.04;
ELSE
	w := LN(x - 4.0) - (1.0 - 1.0/LN(x)) * LN(LN(x));
END_IF;
(* use estimate to calculate exact result *)
FOR i := 0 TO 5 DO
	ewx := EXP(w);
	we := w * ewx - x;
	w1e := (w+1.0) * ewx;
	last := _REAL_TO_DWORD(w) AND DWORD#16#FFFF_FFFC;
	w := w - (we / (w1e - (w+2.0) * we / (2.0 * w + 2.0)));
	IF (_REAL_TO_DWORD(w) AND DWORD#16#FFFF_FFFC) = last THEN EXIT; END_IF;
END_FOR;
LAMBERT_W := w;


(* revision hisdtory
hm	26. oct. 2008	rev 1.0
	original version

hm	10. mar. 2009	rev 1.1
	real constants updated to new systax using dot

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
