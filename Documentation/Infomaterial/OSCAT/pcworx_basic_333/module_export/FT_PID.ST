(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 2.1	11. mar. 2009
programmer 	hugo
tested by	tobias

FT_PI is a PI controller.
The PID controller works according to the fomula Y = IN *(KP+ KI * INTEG(e) ).
a rst will reset the integrator to 0
ilim_h and iLim_l set the possible output range of the internal integrator.
the output flags lim will signal that the output limits are active.

default values for KP = 1, KI = 1, ILIM_L = -1E37, iLIM_H = +1E38.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_PID

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	KP :	REAL := 1.0;
	TN :	REAL := 1.0;
	TV :	REAL := 1.0;
	ILIM_L :	REAL := -1.0E38;
	ILIM_H :	REAL := 1.0E38;
	IEN :	BOOL := TRUE;
	RST :	BOOL := FALSE;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	LIM :	BOOL;
END_VAR


VAR
	integ :	FT_INT;
	diff :	FT_DERIV;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_PID
IEC_LANGUAGE: ST
*)
(* run integrator only if TN > 0 *)
IF TN > 0.0 THEN
	integ(IN := IN, K := 1.0 / TN, RUN := IEN, RST := RST, OUT_MIN := ILIM_L, OUT_MAX := ILIM_H);
ELSE
	integ(RST := FALSE);
END_IF;

(* run differentiator *)
diff(IN := IN, K := TV);

(* combine both values *)
Y := KP * (integ.Out + diff.out + IN);

(* check if integrator has reached its limits and set overflow *)
LIM := integ.LIM;



(* revision history
hm 3. jun. 2008 	rev 2.0
	original version

hm	11. mar. 2009	rev 2.1
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
