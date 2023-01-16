(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.CONTROL
*)
(*@KEY@:DESCRIPTION*)
version 2.2	10. mar. 2009
programmer 	hugo
tested by	oscat

FT_int is an integrator with input IN and factor K.
integration is only done while run = true, if run is false integration is stopped and the out remains at the last value.
if run is left unconnected, run is considered true by the function block.
the output ET will display the total integration time from last reset.
the out_min and out_max values can be set to ,imit the output value range. 
the default for K is 1.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FT_INT

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	K :	REAL := 1.0;
	RUN :	BOOL := TRUE;
	RST :	BOOL;
	OUT_MIN :	REAL := REAL#-1.0E-37;
	OUT_MAX :	REAL := REAL#1.0E37;
END_VAR


VAR_OUTPUT
	OUT :	REAL;
	LIM :	BOOL;
END_VAR


VAR
	INTEG :	INTEGRATE;
END_VAR


(*@KEY@: WORKSHEET
NAME: FT_INT
IEC_LANGUAGE: ST
*)
IF rst THEN
	out := 0.0;
ELSE
	integ(X := IN, E := RUN, K := K, Y := out);
	out := integ.Y;
END_IF;

(* limit the outputs *)
IF out >= OUT_MAX THEN
	out := out_max;
	LIM := TRUE;
ELSIF out <= out_min THEN
	out := out_min;
	lim := TRUE;
ELSE
	lim := FALSE;
END_IF;


(*
hm 13.12.2006	rev 1.1
	changed to "trapezregel" which increases accuracy
	before out := out + in * time new: out := out + (in + in_last) / 2 * time

hm 15.1.2007		rev 1.2
	added default for k to be 1.

hm	15.9.2007		rev 1.3
	replaced time() with T_PLC_US for compatibility and performance reason
	increased internal accuracy to microseconds

hm 29. oct 2007		rev 1.4
	changed code so int will not be called is time difference is 0 to increase accuracy on systems
	with cycle times below 1ms

hm	2. dec 2007	 	rev 1.5
	changed code for better performance

hm	5. jan 2008		rev 1.6
	further improvements in performance

hm	8. feb 2008		rev 1.7
	deleted limits +/- 1000 now limit is the range of real
	added variables out1 and out2 to extend the resolution
	corrected an error with elapsed time
	deleted unusfull output ET

hm	13. mar 2008	rev 1.8
	changed preset value out_min to -1e37.
	stop integrator at the limits.

hm	16. mar 2008	rev 1.9
	added type conversion to avoid warning under codesys 3.0

hm	2. jun. 2008	rev 2.0
	rewritten with clear code
	limits can now be set without run

hm	3. nov. 2008	rev 2.1
	optimized code using INTEGRATE and LIMX

hm	10. mar. 2009	rev 2.2
	removed nested comments
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
