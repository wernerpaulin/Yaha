(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 1.4	11. mar. 2009
programmer 	oscat
tested BY	oscat

this signal generator generates a square wave output. The square wave signal is defined by period time (PT), 
amplitude (AM), offset (OS), duty cycle (DC) and a specific delay for the output signal (DL).
The Output waveform will switch between AM/2 + OS and -AM/2 + OS. The DC input specifies ther duty cycle, 
DC = 0 means output is low at all times and 1 means output is high at all times.
The delay input can delay a signal up to PT, this can be useful to synchronize different generators and generate interleaving signals.
in addition to a analog output Out there is a second boolean output Q.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK GEN_SQR

(*Group:Default*)


VAR_INPUT
	PT :	TIME;
	AM :	REAL := REAL#1.0;
	OS :	REAL;
	DC :	REAL := REAL#0.5;
	DL :	REAL;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	Out :	REAL;
END_VAR


VAR
	tx :	TIME;
	last :	TIME;
	init :	BOOL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: GEN_SQR
IEC_LANGUAGE: ST
*)
(* check dc = 1 or 0 *)
IF dc = 0.0 THEN
	out := -am * 0.5 + os;
	Q := FALSE;
	RETURN;
ELSIF dc = 1.0 THEN
	out := am * 0.5 + os;
	Q := TRUE;
	RETURN;
END_IF;

(* read system time and prepare input data *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS) - last;
DL := modR(dl,1.0);
IF dl < 0.0 THEN dl := 1.0 - dl; END_IF;
dc := modR(dc,1.0);
IF dc < 0.0 THEN dc := 1.0 - dc; END_IF;

(* init section *)
IF NOT init THEN
	init := TRUE;
	last := tx;
	tx := t#0s;
END_IF;

(* add last if one cycle is finished *)
IF tx >= pt THEN
	last := last + pt;
	tx := tx - pt;
END_IF;

(* check if falling or rising edge first *)
IF multime(pt, dl + dc) >= pt THEN
	(* generate falling edge *)
	IF tx >= multime(pt, dl + dc - 1.0) THEN
		out := -am * 0.5 + os;
		Q := FALSE;
	END_IF;
	(* generate rising edge *)
	IF tx >= multime(pt, dl) THEN
		out := am * 0.5 + os;
		Q := TRUE;
	END_IF;
ELSE
	(* generate rising edge first *)
	IF tx >= multime(pt, dl) THEN
		out := am * 0.5 + os;
		Q := TRUE;
	END_IF;
	(* generate falling edge *)
	IF tx >= multime(pt, dl + dc) THEN
		out := -am * 0.5 +os;
		Q := FALSE;
	END_IF;
END_IF;

(* revision history

hm	12. feb 2007	rev 1.1
	added default value for dc = 0.5

hm	17 sep 2007	rev 1.2
	replaced time() with t_plc_ms for compatibilitx reasons

hm	6. jan 2008	rev 1.3
	improved performance

hm	11. mar. 2009	rev 1.4
	changed real constants to use dot syntax
	set default amplitude to 1.0

*)

(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
