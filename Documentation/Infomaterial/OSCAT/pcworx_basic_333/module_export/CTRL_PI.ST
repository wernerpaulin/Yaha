(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 2.0	30. jun. 2008
programmer 	hugo
tested by	oscat

FT_PI is a PI controller with manual functionality.
The PID controller works according to the fomula Y = e *(KP+ KI * INTEG(e) ) + offset, while e = set_point - actual.
a rst will reset all internal data, while a switch to manual will cause the controller to follow the function Y = manual_in + offset.
limit_h and Limit_l set the possible output range of Y.
the output flags lim will signal that the output limits are active and overflow will signal that the integrator has reached its limits.

since rev 1.1 the "trapezregel is used for more accuracy.
rev 1.2 added selective integratin which means the integrative component is only active within a small range of the target value 
this avoids the integrator to go to limits while an input setpoint change happened and is only causing overshoots.
the int_band is by default 100 which means the int is active all the time and if set to for example to 0.1 the integrator is only active
while the input is between 0.9 and 1.1 of the set_point value.

default values for KP = 1, TN = 1, TV = 1, LIMIT_L = -1000, LIMIT_H = +1000.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CTRL_PI

(*Group:Default*)


VAR_INPUT
	ACT :	REAL;
	SET :	REAL;
	SUP :	REAL;
	OFS :	REAL;
	M_I :	REAL;
	MAN :	BOOL;
	RST :	BOOL := FALSE;
	KP :	REAL := 1.0;
	KI :	REAL := 1.0;
	LL :	REAL := -1000.0;
	LH :	REAL := 1000.0;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	DIFF :	REAL;
	LIM :	BOOL;
END_VAR


VAR
	pi :	FT_PIWL;
	co :	CTRL_OUT;
END_VAR


(*@KEY@: WORKSHEET
NAME: CTRL_PI
IEC_LANGUAGE: ST
*)
DIFF := CTRL_IN(SET, ACT, SUP);
pi(in := DIFF, kp := KP, ki := KI, lim_l := LL, lim_h := LH, rst := RST);
co(ci := pi.Y, OFFSET := OFS, man_in := M_I, lim_l := LL, lim_h := LH, manual := MAN);
Y := co.Y;
LIM := co.LIM;

(* revision history
hm 	31.10.2007 	rev 1.0
	original version

hm	3.11.2007	rev 1.1
	added noise input to filter noise
	added output diff
	set limit output false when output is within limits
	overfolw was not set correctly

hm	5. jan 2008	rev 1.2
	improved performance

hm	30. jun. 2008	rev 2.0
	rewritten using new modular approach*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
