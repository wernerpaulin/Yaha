(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.AUTOMATION
*)
(*@KEY@:DESCRIPTION*)
version 1.0	28. jun. 2008
programmer 	hugo
tested by	oscat

FLOW_CONTROL switches a valves depending on the input in.
flow control also limits the maximum ontime of the valve and controls pressure on the output side.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK FLOW_CONTROL

(*Group:Default*)


VAR_INPUT
	IN :	BOOL;
	REQ :	BOOL;
	ENQ :	BOOL;
	RST :	BOOL := FALSE;
	T_AUTO :	TIME := T#1h;
	T_DELAY :	TIME := T#23h;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	STATUS :	BYTE;
END_VAR


VAR
	timer :	TP_1D;
END_VAR


(*@KEY@: WORKSHEET
NAME: FLOW_CONTROL
IEC_LANGUAGE: ST
*)
STATUS := BYTE#100;
IF RST THEN
	Q := FALSE;
	timer(rst := TRUE);
	timer.RST := FALSE;
	STATUS := BYTE#103;
ELSIF ENQ THEN
	IF IN THEN
		status := BYTE#101;
	END_IF;
	IF REQ THEN
		(* timer will generate a timed pulse after TP goes high *)
		timer.PT1 := T_AUTO;
		timer.PTD := T_DELAY;
		timer.IN := TRUE;
		STATUS := BYTE#102;
	END_IF;
END_IF;

(* set output and run timer *)
timer();
timer.IN := FALSE;
Q := (IN AND ENQ) OR timer.Q;

(* revision history
hm 	28. jun. 2008 	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
