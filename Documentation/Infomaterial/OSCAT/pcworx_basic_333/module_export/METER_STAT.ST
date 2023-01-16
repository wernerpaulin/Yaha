(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.MEASUREMENTS
*)
(*@KEY@:DESCRIPTION*)
version 1.3	18. jul. 2009
programmer 	oscat
tested BY	oscat

METER_STAT runs statistics of a metered value, it calculates the current week, day, month and year consumption and stores the corresponding last day, week, month and year value.


(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK METER_STAT

(*Group:Default*)


VAR_INPUT
	IN :	REAL;
	DI :	UDINT;
	RST :	BOOL;
END_VAR


VAR_IN_OUT
	LAST_DAY :	REAL;
	CURRENT_DAY :	REAL;
	LAST_WEEK :	REAL;
	CURRENT_WEEK :	REAL;
	LAST_MONTH :	REAL;
	CURRENT_MONTH :	REAL;
	LAST_YEAR :	REAL;
	CURRENT_YEAR :	REAL;
END_VAR


VAR RETAIN 
	year_start :	REAL;
	month_start :	REAL;
	week_start :	REAL;
	day_start :	REAL;
	last_run :	UDINT;
END_VAR


(*@KEY@: WORKSHEET
NAME: METER_STAT
IEC_LANGUAGE: ST
*)
IF rst THEN
	Last_Day := 0.0;
	Current_Day := 0.0;
	Day_start := IN;
	Last_week := 0.0;
	Current_week := 0.0;
	Week_start := in;
	Last_month := 0.0;
	Current_month := 0.0;
	month_start := in;
	last_year := 0.0;
	current_year := 0.0;
	year_start := in;
ELSE
	Current_Day := IN - Day_Start;
	Current_Week := In - Week_Start;
	Current_Month := IN - Month_Start;
	Current_Year := IN - Year_Start;
END_IF;

IF YEAR_OF_DATE(DI) > YEAR_OF_DATE(last_run) THEN
	(* a new year has started *)
	last_year := current_year;
	current_year := 0.0;
	year_start := in;
	last_month := current_month;
	current_month := 0.0;
	month_start := in;
	last_day := current_day;
	current_day := 0.0;
	day_start := in;
ELSIF MONTH_OF_DATE(DI) > MONTH_OF_DATE(last_run) THEN
	(* a new month has started, january is alrerady done by year change *)
	last_month := current_month;
	current_month := 0.0;
	month_start := in;
	last_day := current_day;
	current_day := 0.0;
	day_start := in;
ELSIF DAY_OF_YEAR(di) > DAY_OF_YEAR(last_run) THEN
	(* day has chaged, first day of year and first day of month has already been taken care of *)
	last_day := current_day;
	current_day := 0.0;
	day_start := in;
END_IF;
IF DAY_OF_WEEK(DI) < DAY_OF_WEEK(last_run) THEN
	(* a new week has started *)
	last_week := current_week;
	current_week := 0.0;
	week_start := in;
END_IF;
last_run := di;

(* revision history
hm	16. sep. 2007	rev 1.0
	original version

hm	7. oct. 2008	rev 1.1
	changed function year_to_year_of_date
	changed function month to month_of_date
	changed function weekday to day_of_week

hm	11. mar. 2009	rev 1.2
	changed real constants to use dot syntax

hm	18. jul. 2009	rev 1.3
	changes all outputs to be I/O
*)


(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
