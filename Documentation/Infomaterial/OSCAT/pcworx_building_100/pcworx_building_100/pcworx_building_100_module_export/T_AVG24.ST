(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: HLK
*)
(*@KEY@:DESCRIPTION*)
version 1.2	13. mar. 2009
programmer 	hugo
tested by	oscat

this function calculates the averaged daytime temperature by taking 48 samples over one day.
a trigger tp will be true for one cycle when the output is updated.
using the input scale the outputs can be adjusted to different scales.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK T_AVG24

(*Group:Default*)


VAR_INPUT
	TS :	INT;
	DTI :	UDINT;
	RST :	BOOL;
	T_FILTER :	TIME := T#10m;
	SCALE :	REAL := 1.0;
	OFS :	REAL;
END_VAR


VAR_OUTPUT
	TA :	REAL;
	TP :	BOOL;
END_VAR


VAR_IN_OUT
	T24 :	REAL;
	T24_MAX :	REAL;
	T24_MIN :	REAL;
END_VAR


VAR
	samples :	oscat_T_AVG24;
	pos :	INT;
	init :	BOOL;
	ft1 :	FILTER_I;
	sum :	DINT;
	last :	UDINT;
	tmp_max :	INT;
	tmp_min :	INT;
	i :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: T_AVG24
IEC_LANGUAGE: ST
*)
(* first filter the sensor readings *)
ft1(X := TS, T := T_FILTER);

IF rst OR NOT init THEN
	init := TRUE;
	IF T24 = -1000.0 THEN t24 := INT_TO_REAL(ft1.Y) * 0.1; END_IF;
	FOR pos := 0 TO 47 DO
		samples[pos] := REAL_TO_INT(T24 * 10.0);
	END_FOR;
	pos := 0;
	sum := INT_TO_DINT(samples[0]) * DINT#48;
	(* calculate the output value *)
	TA := (INT_TO_REAL(ft1.Y) * 0.1 + OFS) * SCALE;
	T24 := (DINT_TO_REAL(sum) * 0.00208333333333 + OFS) * SCALE;
	tp := TRUE;
ELSIF (dti / UDINT#60 MOD UDINT#30) = UDINT#0 AND DTI > last THEN
	(* make sure we onlyexecute once every 30 mins *)
	last := DTI + TIME_TO_UDINT(T#1m);
	(* sample the temperature every 30 mins and store in ring buffer samples *)
	(* sum always holds the sum of the array *)
	(* subtract the oldest sample from sum *)
	sum := sum - INT_TO_DINT(samples[pos]);
	(* strore the new sample *)
	samples[pos] := ft1.Y;
	(* add the new sample to sum *)
	sum := sum + INT_TO_DINT(samples[pos]);
	(* increment the counter for the next sample *)
	pos := INC1(pos, 48);
	(* calculate the output value *)
	TA := (INT_TO_REAL(ft1.Y) * 0.1 + OFS) * SCALE;
	T24 := (DINT_TO_REAL(sum) * 0.00208333333333 + OFS) * SCALE;
	(* calculate the min and max over the last 24 hours *)
	tmp_max := -32000;
	tmp_min := 32000;
	FOR i := 0 TO 47 DO
		tmp_max := MAX(tmp_max, samples[i]);
		tmp_min := MIN(tmp_min, samples[i]);
	END_FOR;
	T24_MAX := (INT_TO_REAL(tmp_max) * 0.1 + OFS) * SCALE;
	T24_MIN := (INT_TO_REAL(tmp_min) * 0.1 + OFS) * SCALE;
	tp := TRUE;
ELSE
	tp := FALSE;
END_IF;





(* revision history
hm	3. nov. 2008	rev 1.0
	original version

hm	8. feb. 2009	rev 1.1
	changes sign of OFS
	added outputs t24_min and t24_max

hm	13. mar. 2009	rev 1.2
	improved code
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
