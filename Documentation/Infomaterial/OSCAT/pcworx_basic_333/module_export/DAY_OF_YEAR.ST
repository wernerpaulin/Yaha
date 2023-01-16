(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.4		28. jan. 2011
programmer 		hugo
tested by		oscat

calculates the day of the year

(*@KEY@:END_DESCRIPTION*)
FUNCTION DAY_OF_YEAR:INT

(*Group:Default*)


VAR_INPUT
	IDATE :	UDINT;
END_VAR


(*@KEY@: WORKSHEET
NAME: DAY_OF_YEAR
IEC_LANGUAGE: ST
*)
DAY_OF_YEAR := UDINT_TO_INT((DATE_TO_UDINT(idate) / UDINT#86400) MOD UDINT#1461);
IF DAY_OF_YEAR > 729 THEN
	IF DAY_OF_YEAR > 1095 THEN DAY_OF_YEAR := DAY_OF_YEAR - 1095; ELSE DAY_OF_YEAR := DAY_OF_YEAR - 729; END_IF;
ELSIF DAY_OF_YEAR > 364 THEN
	DAY_OF_YEAR := DAY_OF_YEAR - 364;
ELSE
	DAY_OF_YEAR := DAY_OF_YEAR + 1;
END_IF;


(*
DAY_OF_YEAR := DWORD_TO_INT((DATE_TO_DWORD(idate) - DATE_TO_DWORD(YEAR_BEGIN(YEAR_OF_DATE(idate)))) / 86400) + 1;
*)


(* revivision history
hm	4. aug. 2007		rev 1.0
	original version

hm	1. oct. 2007		rev 1.1
	added compatibility to STEP7

hm	4. jan. 2008		rev 1.2
	changed code for better performance

hm	7. oct. 2008		rev 1.3
	changed name of function year to year_of_date

hm	28. jan. 2011	rev 1.4
	improved code
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION
