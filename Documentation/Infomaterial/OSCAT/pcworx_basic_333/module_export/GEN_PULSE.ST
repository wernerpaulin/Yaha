(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 1.5	8. apr. 2011
programmer 	hugo
tested by	oscat

GEN_PULSE uses the internal sps timer to generate a continuous output waveform with programmable high and low time.
the accuracy of gen_pulse is depending on the system timer.
when time is 0 the high and low times are exactly one cycle.
ENQ = TRUE will start and ENQ = FALSE will stop the generator.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK GEN_PULSE

(*Group:Default*)


VAR_INPUT
	ENQ :	BOOL := TRUE;
	PTH :	TIME;
	PTL :	TIME;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
END_VAR


VAR
	T_PLC_MS :	T_PLC_MS;
	tx :	TIME;
	tn :	TIME;
	init :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: GEN_PULSE
IEC_LANGUAGE: ST
*)
IF enq THEN
	T_PLC_MS();	(* read system timer *)
	tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);
	IF NOT init THEN init := TRUE; tn := tx; END_IF;
	IF tx - tn >= SEL(Q, PTL, PTH) THEN
		tn := tn + SEL(Q, PTL, PTH);
		Q := NOT Q;
	END_IF;
ELSE
	Q := FALSE;
	init := FALSE;
END_IF;

(* revision history
hm	29. jun. 2008	rev 1.0
	original version

hm	23. nov. 2008	rev 1.1
	set default for enq to be true

hm	18. jul. 2009	rev 1.2
	improved performance

hm	13. nov. 2009	rev 1.3
	corrected error

hm	16. feb. 2011	rev 1.4
	corrected an error when timer overflows

hm	8. apr. 2011	rev 1.5
	ptl and pth was exchanged
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
