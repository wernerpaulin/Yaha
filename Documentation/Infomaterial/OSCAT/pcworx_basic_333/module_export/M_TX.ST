(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.MEASUREMENTS
*)
(*@KEY@:DESCRIPTION*)
version 1.4	11. mar. 2009
programmer 	oscat
tested BY	oscat

this measures the timing of a signal
TH is the high pulse width
TL is the low pulse width
DC is the duty cycle
F is the frequency
ET will start at 0 with a rising edge and count up till the next rising edge starts from 0 again. 
the acuracy depends on the cycle time of the sps and is limited to 1ms resolution.
an asynchronous reset can reset all outputs to 0 at any time.
the input tmax can configure a timeout for ET where the function block will outomatically reset itself.
tmx is predefined to 10 days.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK M_TX

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	TMAX :	TIME := t#10d;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	TH :	TIME;
	TL :	TIME;
	DC :	REAL;
	F :	REAL;
	ET :	TIME;
END_VAR


VAR
	edge :	BOOL;
	start :	TIME;
	stop :	TIME;
	tx :	TIME;
	rise :	BOOL;
	fall :	BOOL;
	startup :	BOOL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: M_TX
IEC_LANGUAGE: ST
*)
(* check FOR rst input *)
IF rst OR (et >= tmax) THEN
	rise := FALSE;
	fall := FALSE;
	startup := FALSE;
	th := t#0ms;
	tl := t#0ms;
	DC := 0.0;
	F := 0.0;
	ET := t#0s;
END_IF;

(* avoid timers to start when input is true at startup *)
IF NOT startup THEN
	edge := in;
	startup := TRUE;
END_IF;

(* read system timer *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* edge trigger rising and falling edge *)
IF in XOR edge THEN
	edge := in;
	(* rising edge starts measurement *)
	IF in THEN
		start := Tx;
		rise := TRUE;
		IF fall THEN tl := start - stop; END_IF;
		IF th > t#0ms AND tl > t#0ms THEN
			dc := TIME_TO_REAL(th) / TIME_TO_REAL(th+tl);
			f := 1000.0 / TIME_TO_REAL(th + tl);
		END_IF;
	(* falling edge starts second cycle measurement *)
	ELSE
		stop := Tx;
		fall := TRUE;
		IF rise THEN th := stop - start; END_IF;
		IF th > t#0ms AND tl > t#0ms THEN
			dc := TIME_TO_REAL(th) /  TIME_TO_REAL(th+tl);
			f := 1000.0 / TIME_TO_REAL(th + tl);
		END_IF;
	END_IF;
END_IF;
IF rise THEN et := tx - start; END_IF;

(* revision history
hm	4. aug. 2006	rev 1.0
	original version

hm	2. mai. 2007	rev 1.1
	made sure that no undefined values would be measured at startup conditions
	added output et
	added rst input
	added tmax input

hm	16. sep. 2007	rev 1.2
	changes time() to T_plc_ms() for compatibility reasons

hm	27. feb. 2009	rev 1.3
	deleted unnecessary init with 0

hm	11. mar. 2009	rev 1.4
	changed real constants to use dot syntax

*)







(* check FOR rst input *)
IF rst OR (et >= tmax) THEN
	rise := FALSE;
	fall := FALSE;
	startup := FALSE;
	th := t#0ms;
	tl := t#0ms;
	DC := 0.0;
	F := 0.0;
	ET := t#0s;
END_IF;

(* avoid timers to start when input is true at startup *)
IF NOT startup THEN
	edge := in;
	startup := TRUE;
END_IF;

(* read system timer *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* edge trigger rising and falling edge *)
IF in XOR edge THEN
	edge := in;
	(* rising edge starts measurement *)
	IF in THEN
		start := Tx;
		rise := TRUE;
		IF fall THEN tl := start - stop; END_IF;
		IF th > t#0ms AND tl > t#0ms THEN
			dc := TIME_TO_REAL(th) / TIME_TO_REAL(th+tl);
			f := 1000.0 / TIME_TO_REAL(th + tl);
		END_IF;
	(* falling edge starts second cycle measurement *)
	ELSE
		stop := Tx;
		fall := TRUE;
		IF rise THEN th := stop - start; END_IF;
		IF th > t#0ms AND tl > t#0ms THEN
			dc := TIME_TO_REAL(th) /  TIME_TO_REAL(th+tl);
			f := 1000.0 / TIME_TO_REAL(th + tl);
		END_IF;
	END_IF;
END_IF;
IF rise THEN et := tx - start; END_IF;

(* revision history
hm	4. aug. 2006	rev 1.0
	original version

hm	2. mai. 2007	rev 1.1
	made sure that no undefined values would be measured at startup conditions
	added output et
	added rst input
	added tmax input

hm	16. sep. 2007	rev 1.2
	changes time() to T_plc_ms() for compatibility reasons

hm	27. feb. 2009	rev 1.3
	deleted unnecessary init with 0

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
