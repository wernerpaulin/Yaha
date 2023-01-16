(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 1.3	11. mar. 2009
programmer 	hugo
tested by	oscat

FT_PIWL is a PI controller.
The PID controller works according to the fomula Y = IN *(KP+ KI * INTEG(e) ).
a rst will reset the integrator to 0
lim_h and Lim_l set the possible output range of the controller.
the output flag lim will signal that the output limits are active.
the integrator ist equipped with anti wind-up circuitry which limits trhe total output ranke to lim_l and lim_h

default values for KP = 1, KI = 1, ILIM_L = -1E37, iLIM_H = +1E38.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_PIWL

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	KP :	REAL := 1.0;
	KI :	REAL := 1.0;
	LIM_L :	REAL := -1.0E38;
	LIM_H :	REAL := 1.0E38;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	LIM :	BOOL;
END_VAR


VAR
	init :	BOOL;
	tx :	UDINT;
	tc :	REAL;
	t_last :	UDINT;
	in_last :	REAL;
	i :	REAL;
	p :	REAL;
	T_PLC_US :	T_PLC_US;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_PIWL
IEC_LANGUAGE: ST
*)
(* initialize at power_up *)
IF NOT init OR RST THEN
	init := TRUE;
	in_last := in;
	T_PLC_US();
	t_last := T_PLC_US.T_PLC_US;
	i := 0.0;
	tc := 0.0;
ELSE
	(* read last cycle time in Microseconds *)
	T_PLC_US();
	tx := T_PLC_US.T_PLC_US;
	tc := UDINT_TO_REAL(tx - t_last);
	t_last := tx;

	(* calculate proportional part *)
	p := KP * IN;

	(* run integrator *)
	i := (IN + in_last) * 5.0E-7 * KI * tc + i;
	in_last := IN;

	(* calculate output Y *)
	Y := p + i;

	(* check output for limits *)
	IF Y >= LIM_H THEN
		Y := LIM_H;
		IF ki <> 0.0 THEN
			i := LIM_H - p;
		ELSE
			i := 0.0;
		END_IF;
		LIM := TRUE;
	ELSIF Y <= LIM_L THEN
		Y := LIM_L;
		IF ki <> 0.0 THEN
			i := LIM_L - p;
		ELSE
			i := 0.0;
		END_IF;
		LIM := TRUE;
	ELSE
		LIM := FALSE;
	END_IF;
END_IF;





(* revision history
hm 13. jun. 2008 	rev 1.0
	original version

hm	27. oct. 2008	rev 1.1
	integrator will not be adjusted when ki = 0

hm	25. jan 2009	rev 1.2
	module will also work with negative K

hm	11. mar. 2009	rev 1.3
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
