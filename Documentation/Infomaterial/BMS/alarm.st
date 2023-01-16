(********************************************************************
 * COPYRIGHT -- WERNER PAULIN 
 ********************************************************************
 * Program: alarm
 * File: alarm.st
 * Author: asdemo
 * Created: December 27, 2009
 ********************************************************************
 * Implementation of program alarm
 * Features:
 * - very simple: no 'selbst haltung' in case of pending ack
 * - scans all alarm flags and creates summary reaction: 
 	 stop, warning, no reaction
 * Interfaces:
 * - gAlarm.request: alarm bits set by other programs
 * - gAlarm.stop:    set if an alarm is active which is configured to stop
 * - gAlarm.warning: set if an alarm is active which is configured to warning
 * - gAlarm.ack:	 acknowledges an alarm
 ********************************************************************
 * History:
 * Version	Date		Author		Comment
 * V1.00	27.12.09	W. Paulin	created
 ********************************************************************)

PROGRAM _INIT
	(* define reaction for alarms *)
	gAlarm.reaction[ALARM_RECIPE_READ] 				:= ALARM_REACTION_NOTHING;
	gAlarm.reaction[ALARM_RECIPE_WRITE] 			:= ALARM_REACTION_NOTHING;
	gAlarm.reaction[ALARM_RECIPE_NAME_INV] 			:= ALARM_REACTION_NOTHING;
	gAlarm.reaction[ALARM_HEATING_BURNER_TEMP_HIGH] := ALARM_REACTION_STOP;
	gAlarm.reaction[ALARM_HEATING_BOILER_TEMP_HIGH] := ALARM_REACTION_STOP;
	gAlarm.reaction[ALARM_HEATING_NODE_CON_ERROR]   := ALARM_REACTION_NOTHING;
	gAlarm.reaction[ALARM_IRRIGATION_NODE_CON_ERROR]:= ALARM_REACTION_NOTHING;
END_PROGRAM


PROGRAM _CYCLIC
	alarmStop    := FALSE;	(* assume no stop before scan *)
	alarmWarning := FALSE;	(* assume no warning before scan *)
	
	FOR index := 0 TO ALARM_MAX-1 DO
		IF (gAlarm.ack[index] = TRUE) OR (gAlarm.ackBlock = TRUE) THEN
  			gAlarm.request[index] := FALSE;				(* reset alarm if acknowledged *)
			gAlarm.ack[index] := FALSE;
		END_IF;
		
		IF (gAlarm.request[index] = TRUE) THEN
  			CASE gAlarm.reaction[index] OF
			  	ALARM_REACTION_STOP    : alarmStop    := TRUE;
			  	ALARM_REACTION_WARNING : alarmWarning := TRUE;
			END_CASE;
		END_IF;		
	END_FOR;
	gAlarm.ackBlock := FALSE;	(* reset block acknowledge *)
	
	(* update publish alarm reaction *)
	gAlarm.stop		:= alarmStop;
	gAlarm.warning	:= alarmWarning;
END_PROGRAM
