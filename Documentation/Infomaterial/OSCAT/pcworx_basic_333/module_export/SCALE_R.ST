(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_PROCESSING
*)
(*@KEY@:DESCRIPTION*)
version 1.2	11. jan. 2011
programmer 	hugo
tested by	oscat

Scale_R is used to translate and scale a REAL input x to a real output.
the input is limited to I_LO <= X <= I_HI.


(*@KEY@:END_DESCRIPTION*)
FUNCTION SCALE_R:REAL

(*Group:Default*)


VAR_INPUT
	X :	REAL;
	I_LO :	REAL;
	I_HI :	REAL;
	O_LO :	REAL;
	O_HI :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SCALE_R
IEC_LANGUAGE: ST
*)
IF I_LO = I_HI THEN
	SCALE_R := O_LO;
ELSE
	SCALE_R := (O_HI - O_LO) / (I_HI - I_LO) * (LIMIT(I_LO, X, I_HI) - I_LO) + O_LO;
END_IF;

(* revision history
hm	18. may. 2008	rev 1.0
	original version

hm	13. nov. 2008	rev 1.1
	corrected formula for negative gradient

hm	11. jan 2011	rev 1.2
	avoid division by 0

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
