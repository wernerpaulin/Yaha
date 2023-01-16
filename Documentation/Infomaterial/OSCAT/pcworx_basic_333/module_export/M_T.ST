(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.MEASUREMENTS
*)
(*@KEY@:DESCRIPTION*)
version 1.4	10. mar. 2009
programmer 	hugo
tested BY	oscat

m_t measures the with of a high pulse and returs the last measured pulse width on output PT.
a second output ET is starting from 0 at the rising edge and counting up until the falling edge occurs and resetts et to 0.
the asynchrtonous input rst can reset the outputs at any time.
tmax defines a maximum measurable time, if this value is exceeded the outputs will be reset to 0.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK M_T

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	TMAX :	TIME := t#10d;
	RST :	BOOL;
END_VAR


VAR_OUTPUT
	PT :	TIME;
	ET :	TIME;
END_VAR


VAR
	edge :	BOOL;
	start :	TIME;
	tx :	TIME;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: M_T
IEC_LANGUAGE: ST
*)
(* read system timer *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

IF RST OR ET >= TMAX THEN
	PT := t#0s;
	ET := PT;
ELSIF IN THEN
	IF NOT edge THEN start := tx; END_IF;
	ET := tx - start;
ELSE
	PT := ET;
END_IF;
edge := IN;



(* revision history
hm	4. aug. 2006	rev 1.0
	original version

hm	2. may. 2007	rev 1.1
	added init variable to avoid unreasonable measurement if falling edge occurs first.
	added et (elapsed time) output to count from 0 at rising edge until a falling edge resets et to 0.
	added reset input.

hm	16. sep. 2007	rev 1.2
	changes time() to T_plc_ms() for compatibility reasons

hm	17. dec. 2008	rev 1.3
	code optimized

hm	10. mar. 2009	rev 1.4
	removed nested comments

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
