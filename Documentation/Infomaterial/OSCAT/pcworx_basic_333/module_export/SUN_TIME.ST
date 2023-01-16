(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: TIME_DATE
*)
(*@KEY@:DESCRIPTION*)
version 1.7	25. jan. 2011
programmer 	hugo
tested by	tobias

this FUNCTION block calculates the sun rise, sun set, sun offset at midday sun declination for a given date 
for performance reasons the algorithm has been simplified and is accurate within a few minutes only 
the times are calculated in utc and have to be corrected for the given time zone
this correction is not done within sun_time because it would be a problem on days where dst is enabled or disabled

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK SUN_TIME

(*Group:Default*)


VAR_INPUT
	LATITUDE :	REAL;(*latitude of geographical position*)
	LONGITUDE :	REAL;(*longitude of geographical position*)
	UTC :	UDINT;(*world time*)
	H :	REAL := -0.83333333333;(*heighth above horizon for sunrise*)
END_VAR


VAR_OUTPUT
	MIDDAY :	UDINT;(*astrological midday in hours when sun stand at south direction*)
	SUN_RISE :	UDINT;(*sun rise for current day in local time*)
	SUN_SET :	UDINT;(*sun set for current day in local time*)
	SUN_DECLINATION :	REAL;(*sun declination at midday in degrees*)
END_VAR


VAR
	DK :	REAL;(*sun declination at midday*)
	delta :	UDINT;(*delta from midday for sunrise and sunset*)
	B :	REAL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SUN_TIME
IEC_LANGUAGE: ST
*)
B := latitude * 0.0174532925199433;
MIDDAY := SUN_MIDDAY(longitude, utc);
DK := 0.40954 * SIN(0.0172 * (INT_TO_REAL(DAY_OF_YEAR(utc)) - 79.35));
sun_declination := DEG(DK);
IF sun_declination > 180.0 THEN sun_declination := sun_declination - 360.0; END_IF;
sun_declination := 90.0 - LATITUDE + sun_declination;
delta := TIME_TO_UDINT(HOUR_TO_TIME(ACOS((SIN(RAD(H)) - SIN(B) * SIN(DK)) / (COS(B) * COS(DK))) * 3.819718632));
sun_rise := MIDDAY - delta;
sun_set := MIDDAY + delta;

(* revision history

rev 1.1	hm	20.1.2007
	deleted unused variables sun_riseR and sun_setR

rev 1.2 hm 17.4.2007
	corrected error while sun:midday would not be corrected for longitude.

rev 1.3	hm	6. jan 2008
	performance improvements

rev	1.4 hm	17. jan 2008
	calculation is now only performed once a day

hm	10. mar. 2009	rev 1.5
	improved performance
	calculation will be performed on every call to allow movong installations

hm	26. jul 2009	rev 1.6
	fixed a problem with wrong midday calculation

hm	25. jan. 2011	rev 1.7
	using function sun_midday
	corrected angle of sun_declination
	added input H
*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
