(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.9	27. feb. 2009
programmer 	oscat
tested by	oscat

ltime is a real time clock that uses the system rtc as utc time and calculates and given time zone.
the utc time is supplied on the input UTC.
according to the input variable time_zone_offset when the input dst_enable is true,
the dst on and off times are calculated by a formula for any given year and the time is advanced and reset by one hour
at 02:00 and 03:00 for the last sunday of march and last sunday of october.
the code is high performance and the rtc counts every second.
if more then one time zone is needed by the systen the clock can be started many times by placing more then one function block.
(*@KEY@:END_DESCRIPTION*)
FUNCTION UTC_TO_LTIME:UDINT

(*Group:Default*)


VAR_INPUT
	UTC :	UDINT;
	DST_ENABLE :	BOOL;
	TIME_ZONE_OFFSET :	INT;
END_VAR


VAR
	tmp :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: UTC_TO_LTIME
IEC_LANGUAGE: ST
*)
UTC_TO_LTIME := UTC + _INT_TO_UDINT(TIME_ZONE_OFFSET) * UDINT#60 + BOOL_TO_UDINT(DST_ENABLE AND DST(UTC)) * UDINT#3600;


tmp := TIME_ZONE_OFFSET * 60 + BOOL_TO_INT(DST_ENABLE AND DST(UTC)) * 3600;
IF tmp < 0 THEN
	UTC_TO_LTIME := UTC - _INT_TO_UDINT(ABS(tmp));
ELSE
	UTC_TO_LTIME := UTC + _INT_TO_UDINT(tmp);
END_IF;


(* revision history

hm 2.10.2006	rev 1.1
	corrected an error where dst would be delayed by 0.1second

hm 17.1.2007	rev 1.2
	added utc input instead of internal sysrtcgettime because this would only work on wago.
	dst_enable would not be checked before dst would be enabled.

hm 18.3.2007	rev 1.3
	changed code, dst would not work during first cycle.

hm 24.10.2007	rev 1.4
	changed code because the execution every 100ms can cause major problems if the supplied time was not correct at start.
	use of new dst function

hm 12. nov 2007	rev 1.5
		changed Type of time_zone_offset from time to int to allow for time zones with negative offset

hm	8 dec 2007		rev 1.6
	corrected a problem with time_zone_offset

hm	14. oct. 2008	rev 1.7
	renamed module from LTIME to UTC_TO_LTIME
	changed function weekday to day_of_week
	optimized code for better performance

hm	20. oct. 2008	rev 1.8
	changes type of input TIME_ZONE_OFFSET from real to int, now is in +/-minutes
	deleted outputs DST_ON and WDAY
	converted to function

hm	27. feb. 2009	rev 1.9
	added type conversions to avoid warnings under codesys 3.0

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
