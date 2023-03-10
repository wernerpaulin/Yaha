(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ELECTRICAL
*)
(*@KEY@:DESCRIPTION*)
version 2.3	26. jan. 2009
programmer 	hugo
tested by	tobias

this is an intelligent dimmer interface with an autoset feature for "in" it will automatically detect the type of switch:
low active pulses or high high active pulses are allowd for in.
a configurable debounce timer will debounce input signals
if t_on_max is set to anything other then 0 the output will be turned off after the max on time is reached.
the times for debounce, dimming ramp, wait time before dimming and max on time are all programmable.

the dimmer has outputs Q for on and off and also out with the analog dimm value.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK DIMM_I

(*Group:Default*)


VAR_INPUT
	SET :	BOOL;
	VAL :	BYTE := BYTE#255;
	IN :	BOOL;
	RST :	BOOL;
	T_DEBOUNCE :	TIME := T#10ms;
	T_RECONFIG :	TIME := T#10s;
	T_ON_MAX :	TIME := T#0h;
	T_DIMM_START :	TIME := T#1s;
	T_DIMM :	TIME := T#3s;
	MIN_ON :	BYTE := BYTE#50;
	MAX_ON :	BYTE := BYTE#255;
	SOFT_DIMM :	BOOL := TRUE;
	DBL_TOGGLE :	BOOL;
	RST_OUT :	BOOL;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	DBL :	BOOL;
END_VAR


VAR_IN_OUT
	OUT :	BYTE := BYTE#0;
END_VAR


VAR
	config :	SW_RECONFIG;
	decode :	CLICK_MODE;
	t3 :	TON;
	dim :	_RMP_B;
	dir :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: DIMM_I
IEC_LANGUAGE: ST
*)
(* the input is first sent through auto reconfiguration and debouncing *)
config(IN := IN, TD := T_DEBOUNCE, TR := T_RECONFIG);
decode(in := config.Q, T_LONG := T_DIMM_START);

IF RST THEN
	IF rst_out THEN out := BYTE#0; END_IF;
	Q := FALSE;
	dir := out > BYTE#127;
ELSIF set THEN
	out := val;
	Q := TRUE;
	(* set direction to up when value < 127 otherwise set dir down dir is reversed because next action will reverse again *)
	dir := out > BYTE#127;
ELSIF decode.SINGLE THEN
	(* a single click reverses output Q *)
	Q := NOT Q;
	(* when dimmer is turned on we need to limit out to min and max limits *)
	IF Q THEN OUT := INT_TO_BYTE(LIMIT_INT(MAX(_BYTE_TO_INT(MIN_ON),1), _BYTE_TO_INT(out), _BYTE_TO_INT(MAX_ON)));	END_IF;
	(* set the appropriate direction of dimmer dir is reversed because next action will reverse again *)
	dir := OUT > BYTE#127;
ELSIF decode.TP_LONG THEN
	IF NOT Q THEN
		IF SOFT_DIMM THEN
			OUT := BYTE#1;
			dir := TRUE;
		ELSE
            out := INT_TO_BYTE(LIMIT_INT(MAX(_BYTE_TO_INT(MIN_ON),1), _BYTE_TO_INT(out), _BYTE_TO_INT(MAX_ON)));
			DIR := out < BYTE#127;
		END_IF;
		Q := TRUE;
	ELSE
		(* reverse direction with every long click *)
		dir := NOT dir;
	END_IF;
END_IF;

(* set the double click output *)
IF NOT dbl_toggle THEN dbl := FALSE; END_IF;
IF decode.DOUBLE THEN dbl := NOT dbl; END_IF;

(* while dimming is active ramp the output out up or down *)
dim(DIR := dir, e := decode.LONG AND Q, TR := T_DIMM, rmp := out);
OUT := dim.RMP;
(* reverse direction when limits are reached *)
IF out = BYTE#0 THEN
	dir := TRUE;
ELSIF out = BYTE#255 THEN
	dir := FALSE;
END_IF;

(* limit the maximum runtime *)
IF t_ON_MAX > t#0s THEN
	t3(in := q, pt := T_ON_MAX);
	Q := Q XOR t3.Q;
END_IF;

(* revision history

hm 22.1.2007		rev 1.1
	deleted unused structure ramp

hm 2.feb 2007		rev 1.2
	changed structure to read time() at the beginning for better time consistency if a higher priorized tak interrupts dimm_i
	added statements in case structure for state 1 to allow for short 1 cycle input pulses

hm 	15.9.2007		rev 1.3
	replaced Time() with T_PLC_MS for compatibility and performance reasons

hm	30. sep. 2008	rev 1.4
	added Input VAL to supply value for set input
	added setup parameter init_val

hm	22. oct. 2008	rev 2.0
	new code and features

hm	14. nov. 2008	rev 2.1
	added soft_dimm feature

hm	16. nov. 2008	rev 2.2
	added reset out feature

hm	26. jan. 2009	rev 2.3
	dimming will also reverse at out = 0
	rst will override set
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
