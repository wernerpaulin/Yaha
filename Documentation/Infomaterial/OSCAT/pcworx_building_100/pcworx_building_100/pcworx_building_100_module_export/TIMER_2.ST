(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ELECTRICAL
*)
(*@KEY@:DESCRIPTION*)
version 1.5	22.dec.2008
programmer 	oscat
tested by	oscat

this timer generated programmabe output pulses per day, week, month and so on.
the mode input determines on which days the timer will be active.
	mode = 0			never
	mode = 1..7			monday .. sunday
	mode = 11			every day
	mode = 12			every second day
	mode = 13			every 3rd day
	mode = 14			every 4th day
	mode = 15			every 5th day
	mode = 16 			every 6th day
	mode = 20			only monday - friday
	mode = 21			only sat - sunday
	mode = 22			workdays only
	mode = 23			holidays and weekend
	mode = 24			holidays only
	mode = 25			every 1st day of the month
	mode = 26			every last day of the month
	mode = 27			every 31 of december
	mode = 28			every 1st of january

a holiday input can be used to supply holiday information to the module.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK TIMER_2

(*Group:Default*)


VAR_INPUT
	DT_IN :	UDINT;
	START :	UDINT;
	DURATION :	TIME;
	MODE :	BYTE;
	HOLIDAY :	BOOL;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
END_VAR


VAR
	last_check :	TIME := T#0s;
	dat :	UDINT;
	daytime :	UDINT;
	activation :	TIME;
	tx :	TIME;
	enabled :	BOOL;
	wday :	INT;
	init :	BOOL;
END_VAR


VAR RETAIN 
	run_date :	UDINT;
END_VAR


VAR
	T_PLC_MS :	T_PLC_MS;
END_VAR


(*@KEY@: WORKSHEET
NAME: TIMER_2
IEC_LANGUAGE: ST
*)
(* read system time *)
T_PLC_MS();
tx:= UDINT_TO_TIME(T_PLC_MS.T_PLC_MS);

IF NOT init THEN
	init := TRUE;
	last_check := tx - t#100ms;
END_IF;

(* for performance resons exit if execution is not necessary *)
IF tx - last_check < T#100ms THEN RETURN; END_IF;

(* calculate temp variables *)
dat := DT_TO_DATE(dt_in);
daytime := DT_TO_TOD(dt_in);
wday := DAY_OF_WEEK(dat);

(* calculate if any action is necessary today *)
CASE _BYTE_TO_INT(mode) OF
1..7:	(* mondays to fridays *)
	enabled := wday = _BYTE_TO_INT(mode);
11:	(* every day *)
	enabled := TRUE;
12..16:	(* every nth day *)
	enabled := (dat / UDINT#86400) MOD (BYTE_TO_UDINT(mode) - UDINT#10) = UDINT#0;
20:	(* monday - friday *)
	enabled := wday <= 5;
21:	(* saturday and sunday *)
	enabled := wday > 5;
22: (* workdays only *)
	enabled := wday <= 5 AND NOT holiday;
23:	(* holidays and weekends *)
	enabled := wday > 5 OR holiday;
24:	(* holidays only *)
	enabled := holiday;
25:	(* 1st day of the month *)
	enabled := DAY_OF_MONTH(dat) = 1;
26:	(* last day of month *)
	enabled := day_of_month(dat + TIME_TO_UDINT(t#1d)) = 1;
27:	(* 31st of december *)
	enabled := DAY_OF_MONTH(dat) = 31 AND MONTH_OF_DATE(dat) = 12;
28:	(* 1st of january *)
	enabled := DAY_OF_YEAR(dat) = 1;
ELSE
	enabled := FALSE;
END_CASE;

(* set output if necessary *)
IF enabled AND NOT Q AND daytime >= start AND run_date <> dat THEN
	Q := TRUE;
	activation := tx;
	run_date := dat;
ELSIF Q AND tx - activation >= duration THEN
	Q := FALSE;
END_IF;
last_check := Tx;


(* revision history
hm 22.2.2007		rev 1.1
	changed VAR RETAIN PERSISTENT to VAR RETAIN for better compatibility
	wago lon contollers do not support persisitent

hm	15.9.2007		rev 1.2
	replaced Time() with T_PLC_MS for compatibility and performance reasons

hm	7. oct. 2008	rev 1.3
	changed function month to month_of_date

hm	20. oct. 2008	rev 1.4
	improved performance
	deleted unnecessary trunc

hm	22. dec. 2008	rev 1.5
	make sure timer_2 is executed in the first cycle

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
