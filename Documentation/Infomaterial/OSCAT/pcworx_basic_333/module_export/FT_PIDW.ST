(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 1.2	11. mar. 2009
programmer 	hugo
tested by	oscat

FT_PIDW is a PID controller with dynamic wind_up reset.
The PID controller works according to the fomula Y = KP *(IN + KI * INTEG(e) + DERIV(e) ).
a rst will reset the integrator to 0
lim_h and Lim_l set the possible output range of the internal integrator.
the output flags lim will signal that the output limits are active.

default values for KP = 1, KI = 1, ILIM_L = -1E37, iLIM_H = +1E38.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_PIDW

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	KP :	REAL := 1.0;
	TN :	REAL := 1.0;
	TV :	REAL := 1.0;
	LIM_L :	REAL := -1.0E38;
	LIM_H :	REAL := 1.0E38;
	RST :	BOOL := FALSE;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	LIM :	BOOL;
END_VAR


VAR
	integ :	INTEGRATE;
	diff :	FT_DERIV;
	YI :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_PIDW
IEC_LANGUAGE: ST
*)
(* run the integrator *)
IF tn = 0.0 OR rst THEN
	integ(E := FALSE, Y := YI);
	YI := integ.Y;
	YI := 0.0;
ELSE
	integ(X := IN, K := 1.0 / TN, E := NOT LIM, Y := YI);
	YI := integ.Y;
END_IF;

(* add up integrator and linear part *)
Y := KP * (IN + YI);

(* run differentiator *)
diff(IN := IN, K := TV);

(* set lim before differentiator is added to stop integrator if necessary *)
IF Y > LIM_L AND Y < LIM_H THEN
	LIM := FALSE;
ELSE
	LIM := TRUE;
END_IF;

(* add differential part and limit output Y *)

Y := LIMIT(LIM_L, Y + KP * diff.out, LIM_H);




(* revision history
hm 3. jun. 2008 	rev 1.0
	original version

hm	5. nov. 2008	rev 1.1
	changed code to use integrate

hm	11. mar. 2009	rev 1.2
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
