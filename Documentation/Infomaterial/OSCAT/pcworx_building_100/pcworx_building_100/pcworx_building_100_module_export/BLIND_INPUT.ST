(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: JALOUSIE
*)
(*@KEY@:DESCRIPTION*)
version 1.7	12. nov. 2009
programmer 	hugo
tested by	oscat
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK BLIND_INPUT

(*Group:Default*)


VAR_INPUT
	POS :	BYTE;
	ANG :	BYTE;
	S1 :	BOOL;
	S2 :	BOOL;
	IN :	BOOL;
	PI :	BYTE;
	AI :	BYTE;
	SINGLE_SWITCH :	BOOL;
	CLICK_EN :	BOOL := TRUE;
	CLICK_TIME :	TIME := T#500ms;
	MAX_RUNTIME :	TIME := T#60s;
	MANUAL_TIMEOUT :	TIME := T#1h;
	DEBOUNCE_TIME :	TIME := T#20ms;
	DBL_CLK1 :	BOOL := FALSE;
	DBL_POS1 :	BYTE;
	DBL_ANG1 :	BYTE;
	DBL_CLK2 :	BOOL := FALSE;
	DBL_POS2 :	BYTE := BYTE#255;
	DBL_ANG2 :	BYTE := BYTE#255;
	D1_TOGGLE :	BOOL := TRUE;
	D2_TOGGLE :	BOOL := TRUE;
	MASTER_MODE :	BOOL;
END_VAR


VAR_OUTPUT
	QU :	BOOL := TRUE;
	QD :	BOOL := TRUE;
	STATUS :	BYTE;
	PO :	BYTE := BYTE#255;
	AO :	BYTE := BYTE#255;
	D1 :	BOOL;
	D2 :	BOOL;
END_VAR


VAR
	s1e :	TOF;
	s2e :	TOF;
	s1d :	CLICK_MODE;
	s2d :	CLICK_MODE;
	dir :	BOOL;
	tx :	TIME;
	last :	TIME;
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: BLIND_INPUT
IEC_LANGUAGE: ST
*)
(* read system Time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

(* inputs S1 and S2 are debounced and then decoded for multiple clicks *)
s1e(in := S1, pt := DEBOUNCE_TIME);
s2e(in := S2, pt := DEBOUNCE_TIME);
s1d(in := (s1e.Q AND NOT SINGLE_SWITCH) OR (s1e.Q AND SINGLE_SWITCH AND dir), t_long := CLICK_TIME);
s2d(in := (s2e.Q AND NOT SINGLE_SWITCH) OR (s1e.Q AND SINGLE_SWITCH AND NOT dir), t_long := CLICK_TIME);

(* if d1 and d2 are not toggle clear them to make sure they are only active for oine cycle *)
IF NOT d1_toggle THEN d1 := FALSE; END_IF;
IF NOT d2_toggle THEN d2 := FALSE; END_IF;

(* decode actions *)
IF (s1d.LONG AND s2d.LONG) OR (status = BYTE#139) THEN
   status := BYTE#139;
   IF NOT (s1d.LONG OR s2d.LONG)  THEN status := BYTE#130; END_IF;
ELSIF s1d.tp_LONG THEN
	status := BYTE#132;
ELSIF s2d.tp_LONG THEN
	status := BYTE#133;
ELSIF  s1d.SINGLE THEN
	IF click_en THEN
		(* if running then we stop otherwise start new direction *)
		IF QU XOR QD THEN
			status := BYTE#131;
		ELSE
			status := BYTE#134;
			last := tx;
			dir := NOT dir;
		END_IF;
	END_IF;
ELSIF  s2d.SINGLE THEN
	IF click_en THEN
		(* if running then we stop otherwise start new direction *)
		IF QU XOR QD THEN
			status := BYTE#131;
		ELSE
			status := BYTE#135;
			last := tx;
			dir := NOT dir;
		END_IF;
	END_IF;
ELSIF in THEN
	status := BYTE#136;
	last := tx;
ELSIF s1d.DOUBLE THEN
	IF dbl_clk1 THEN
		(* a position need to be set for a double click on S1 *)
		status := BYTE#137;
		last := tx;
	ELSE
		(* toggle the output when dbl_clk1 is not active *)
		D1 := NOT D1;
	END_IF;
ELSIF s2d.DOUBLE THEN
	IF dbl_clk2 THEN
		(* a position need to be set for a double click on S2 *)
		status := BYTE#138;
		last := tx;
	ELSE
		(* toggle the output when dbl_clk2 is not active *)
		(* in single switch mode we need to toggle d1 instead of d2 *)
		IF single_switch THEN D1 := NOT D1; ELSE D2 := NOT D2; END_IF;
	END_IF;
END_IF;


(* state machine *)
CASE _BYTE_TO_INT(status) OF
	0:		(* power up operation *)
			status := BYTE#130;

	130:	(* automatic operation standby *)
			IF NOT master_mode THEN
				PO := POS;
				AO := ANG;
			END_IF;
			QU := TRUE;
			QD := TRUE;

	131:	(* manual operation standby *)
			QU := FALSE;
			QD := FALSE;
			PO := POS;
			AO := ANG;
			(* manual mode will be ended when timeout is reached *)
			IF tx - last >= manual_timeout THEN
				status := BYTE#130;
			END_IF;

	132:	(* manual operation up *)
			QU := TRUE;
			QD := FALSE;
			PO := POS; AO := ANG;
			last := tx;
			IF NOT s1d.LONG THEN status := BYTE#131; dir := NOT dir; END_IF;

	133:	(* manual operation down *)
			QU := FALSE;
			QD := TRUE;
			PO := POS; AO := ANG;
			last := tx;
			IF NOT s2d.LONG THEN	status := BYTE#131; dir := NOT dir; END_IF;

	134:	(* manual operation single click up *)
			QU := TRUE;
			QD := FALSE;
			PO := POS; AO := ANG;
			IF tx - last >= max_runtime THEN status := BYTE#131; END_IF;

	135:	(* manual operation single click dn *)
			QU := FALSE;
			QD := TRUE;
			PO := POS; AO := ANG;
			IF tx - last >= max_runtime THEN status := BYTE#131;	END_IF;

	136:	(* forced input in = true *)
			QU := TRUE;
			QD := TRUE;
			PO := PI; AO := AI;
			IF tx-last >= max_runtime THEN status := BYTE#130; END_IF;

	137:	(* double click1 position *)
			QU := TRUE;
			QD := TRUE;
			PO := DBL_POS1;
			AO := DBL_ANG1;
			IF tx - last >= max_runtime THEN status := BYTE#131; END_IF;

	138:	(* double click2 position *)
			QU := TRUE;
			QD := TRUE;
			PO := DBL_POS2;
			AO := DBL_ANG2;
			IF tx - last >= max_runtime THEN status := BYTE#131; END_IF;

	   139:   (* manual operation standby *)
	         QU := FALSE;
	         QD := FALSE;
	         PO := POS;
	         AO := ANG;

END_CASE;


(* revision history
hm	29. sep 2007	rev 1.0
	original release

hm	6. oct 2007		rev 1.1
	renamed ps and as to po and ao

hm	30. dec 2007	rev 1.2
	added click_timeout variable and function

hm	16. jul. 2008	rev 1.3
	rewirtten code to allow for more functionality
	added single click mode with single_switch.
	added Debounce for inputs S1 and S2
	added double_click functionality

hm	26. sep. 2008	rev 1.4
	corrected an error while POS and ANG was transferred to outputs PO and AO during automatic modes

hm	22. jan 2009	rev 1.5
	added pulse mode for double click outputs
	added automatic mode for IN

hm	27. jul 2009	rev 1.6
	changed status 0 to 130

HF	12. nov. 2009	rev 1.7
	added state 139
	set defaults for QU, QD, PO

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
