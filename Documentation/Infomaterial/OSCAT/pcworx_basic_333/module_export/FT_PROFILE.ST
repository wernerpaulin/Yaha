(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.AUTOMATION
*)
(*@KEY@:DESCRIPTION*)
version 1.1	15 sep 2007
programmer 	tobias
tested by	hugo

FT_Profile generates an output signal which is defined by values over a time scale.
the different values are connected by ramps between the individual values.
a rising edge on E starts the output signal generation and E = True can delay time_3 / value_3 as long as it stays true.
an additional multiplier K can be used to multiply the output and an offset O can be added to the output dynamically.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_PROFILE

(*Group:Default*)


VAR_INPUT
	K :	REAL := 1.0;
	O :	REAL := 0.0;
	M :	REAL := 1.0;
	E :	BOOL;
	VALUE_0 :	REAL;
	TIME_1 :	TIME;
	VALUE_1 :	REAL;
	TIME_2 :	TIME;
	VALUE_2 :	REAL;
	TIME_3 :	TIME;
	VALUE_3 :	REAL;
	TIME_10 :	TIME;
	VALUE_10 :	REAL;
	TIME_11 :	TIME;
	VALUE_11 :	REAL;
	TIME_12 :	TIME;
	VALUE_12 :	REAL;
	TIME_13 :	TIME;
	VALUE_13 :	REAL;
END_VAR


VAR_OUTPUT
	Y :	REAL;
	RUN :	BOOL;
	ET :	TIME;
END_VAR


VAR
	tx :	TIME;
	edge :	BOOL;
	state :	INT;
	ta :	TIME;
	tb :	TIME;
	t0 :	TIME;
	temp :	REAL;
	va :	REAL;
	vb :	REAL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_PROFILE
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* determine start condition *)
IF E AND NOT edge THEN
	RUN := TRUE;
	ET := t#0s;
	t0 := tx;
	ta := tx;
	tb := multime(time_1, M);
	va := value_0;
	vb := value_1;
	temp := value_0;
	state := 1;
END_IF;
edge := E;

(* generate startup profile *)
IF run THEN
	CASE state OF
		1:	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_2 - time_1, M);
				va := value_1;
				vb := value_2;
				temp := value_1;
				state := 2;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		2:	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_3 - time_2, M);
				va := value_2;
				vb := value_3;
				temp := value_2;
				state := 3;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		3:	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_10 - time_3, M);
				va := value_3;
				vb := value_10;
				temp := value_3;
				state := 4;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		4 :	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_11 - time_10, M);
				va := value_10;
				vb := value_11;
				temp := value_10;
				IF E THEN state := 5; ELSE state := 6; END_IF;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		5:	(* extend the signal while E is true *)
			IF E THEN
				ta := tx;
			ELSE
				state := 6;
			END_IF;
		6:	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_12 - time_11, M);
				va := value_11;
				vb := value_12;
				temp := value_11;
				state := 7;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		7:	IF tx - ta >= tb THEN
				ta := ta + tb;
				tb := multime(time_13 - time_12, M);
				va := value_12;
				vb := value_13;
				temp := value_12;
				state := 8;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
		8:	IF tx - ta >= tb THEN
				temp := value_13;
				run := FALSE;
			ELSE
				temp := ((vb - va) * TIME_TO_REAL(tx - ta) / TIME_TO_REAL(tb) + va);
			END_IF;
	END_CASE;
	Y := temp * K + O;
	ET := tx - t0;
END_IF;

(* revision history
hm	27 feb 2007		rev 1.0
	original version

hm	15. sep2007		rev 1.1
	replaced Time() with T_PLC_MS for compatibility and performance reasons

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
