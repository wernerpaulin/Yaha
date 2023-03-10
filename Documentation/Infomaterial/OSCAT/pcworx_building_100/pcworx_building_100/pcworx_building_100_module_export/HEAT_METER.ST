(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: HLK
*)
(*@KEY@:DESCRIPTION*)
version 1.10	23. jan. 2011
programmer 		hugo
tested by		oscat

Heat meter measures the heat transfer of water of a mixture of water and another component.
The inputs are foreward temperature and reverse temperature.
the additional component is specified with its parameters density, Specific heat capacity and content in %.
an input e anables the measurement while it can be configured to be based on X liters / pulse or in liters / hour.
the output Y is in Joule.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK HEAT_METER

(*Group:Default*)


VAR_INPUT
	TF :	REAL;
	TR :	REAL;
	LPH :	REAL;
	E :	BOOL;
	RST :	BOOL;
	CP :	REAL;
	DENSITY :	REAL;
	CONTENT :	REAL;
	PULSE_MODE :	BOOL;
	RETURN_METER :	BOOL;
	AVG_TIME :	TIME := T#5s;
END_VAR


VAR_OUTPUT
	C :	REAL;
END_VAR


VAR_IN_OUT
	Y :	REAL;
END_VAR


VAR
	tx :	UDINT;
	last :	UDINT;
	int1 :	FT_INT2;
	edge :	BOOL;
	x :	REAL;
	init :	BOOL;
	Y_last :	REAL;
	T_PLC_MS :	T_PLC_MS;
	WATER_ENTHALPY :	WATER_ENTHALPY;
	wa_TF :	REAL;
	wa_TR :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: HEAT_METER
IEC_LANGUAGE: ST
*)
IF rst THEN
	int1(rst := TRUE);
	int1.rst := FALSE;
	C := 0.0;
	Y := 0.0;
ELSIF e THEN
	water_enthalpy(T:=TF);
	wa_TF:=water_enthalpy.Result;

	water_enthalpy(T:=TR);
	wa_TR:=water_enthalpy.Result;

	X := (WATER_DENSITY(SEL(return_meter, TF, TR), FALSE) * (wa_TF - wa_TR) * (1.0 - content) + CP * Density * content * (TF-TR));
END_IF;

(* integrate or add consumption *)
int1(run := NOT pulse_mode AND e, in := X * LPH * 2.77777777777E-4);
IF pulse_mode THEN
	IF NOT edge AND E THEN Y := Y + X * LPH; END_IF;
ELSE
	Y := int1.Out;
END_IF;

(* store the value of e *)
edge := e;

(* read system_time *)
T_PLC_MS();
tx:= T_PLC_MS.T_PLC_MS;

(* only init at startup necessary *)
IF NOT init THEN
	init := TRUE;
	last := tx;
END_IF;

(* calculate the current consumption *)
IF (tx - last >= TIME_TO_UDINT(AVG_TIME)) AND (avg_time > T#0s) THEN
	last := tx;
	C := (Y - Y_last) * 3.6E12 / TIME_TO_REAL(AVG_TIME);
	Y_last := Y;
END_IF;

(* revision history
hm	16. nov. 2007	rev 1.0
	original version

hm	24. dec. 2007	rev 1.1
	added config variable return_meter
	added output C for current consumption

hm	6. mar. 2008	rev 1.2
	corrected an error in pulse mode

hm	16. mar. 2008	rev 1.3
	added type conversion to avoid warnings under codesys 3.0

hm	21. oct. 2008	rev 1.4
	improved code

hm	6. nov. 2008	rev 1.5
	changed to FT_INT2 to avoid overrun at hig values

hm	8. feb. 2009	rev 1.6
	changes Y to be I/O

hm	23. mar. 2009	rev 1.7
	real constants updated to new systax using dot
	corected error in formula

hm	27. jul 2009	rev 1.8
	output C is now calculated in J/h

hm	13. nov. 2009	rev 1.9
	output C is now calculated correctly

hm	23. jan. 2011	rev 1.10
	corrected an error with pulse_mode
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
