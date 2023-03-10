(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: LOGIC.GENERATORS
*)
(*@KEY@:DESCRIPTION*)
version 1.0	
programmer 	hugo
tested by	oscat
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK CYCLE_4

(*Group:Default*)


VAR_INPUT
	E :	BOOL := TRUE;
	T0 :	TIME;
	T1 :	TIME;
	T2 :	TIME;
	T3 :	TIME;
	S0 :	BOOL;
	SX :	INT;
	SL :	BOOL;
END_VAR


VAR_OUTPUT
	STATE :	INT;
END_VAR


VAR
	tx :	TIME;
	last :	TIME;
	init :	BOOL;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: CYCLE_4
IEC_LANGUAGE: ST
*)
(* read system *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* init on first cycle *)
IF NOT init THEN
	init := TRUE;
	last := tx;
END_IF;

IF E THEN
	IF SL THEN
		(* when sx > 0 then the state sx is forced to start *)
		state:= LIMIT(0,SX,3);
		last := tx;
		(* this is to avoid to reset sx from the calling programm it does work fine on codesys but i am not sure about other systems, because we are writing to an input *)
		SL := FALSE;
	ELSE
		CASE state OF
			0 :	(* wait for T0 and switch to next cycle *)
				IF tx - last >= T0 THEN
					state := 1;
					last := tx;
				END_IF;
			1 : (* wait for T1 over 1st cycle *)
				IF tx - last >= T1 THEN
					state := 2;
					last := tx;
				END_IF;
			2 : (* wait for T1 over 1st cycle *)
				IF tx - last >= T2 THEN
					state := 3;
					last := tx;
				END_IF;
			3 : (* wait for T2 over 2nd cycle *)
				IF tx - last >= T3 THEN
					IF S0 THEN State := 0; END_IF; (* if S0 is false, the sequence stops at state 3 *)
					last := tx;
				END_IF;
		END_CASE;
	END_IF;
ELSE
	state := 0;
	last := tx;
END_IF;



(*
hm	3. nov. 2008	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
