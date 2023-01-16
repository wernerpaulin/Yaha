(********************************************************************
 * COPYRIGHT -- WERNER PAULIN 
 ********************************************************************
 * Program: hs_sim
 * File: hs_sim.st
 * Author: paulinw
 * Created: December 30, 2009
 ********************************************************************
 * Implementation of program hs_sim
 * Features:
 * - simulation of heating system
 * Interfaces:
 * - gActData.heating.hotwater.tempAct
 * - gActData.heating.burner.tempAct
 * - gActData.heating.tempFlowAct
 * - gActData.heating.tempOutsideAct
 * - gActData.heating.tempLivingroomAct
 * - gActData.heating.sActMixer
 * - doBurner
 * - doFlowPump
 * - doBoilerPump
 ********************************************************************
 * History:
 * Version	Date		Author		Comment
 * V1.00	30.12.09	W. Paulin	created
 ********************************************************************)

PROGRAM _INIT
	gSimulation.isActive := TRUE;				(* indicates that this task has been downloaded and simulation is active *)
	gActData.heating.tempOutsideAct := 5.0;		(* fixed but can be changed online *)
	
	gSimulation.updatePID := TRUE;				(* faster PID reaction due to faster plant simulation *)
	gSimulation.kp := 6.0;								
	gSimulation.tn := 30.0;
END_PROGRAM


PROGRAM _CYCLIC
	(* override PID during runtime as default receipe will be loaded during boot up *)
	IF (gSimulation.updatePID = TRUE) THEN
		gSimulation.updatePID := FALSE;
		gHMI.recipe.data.heating.kp := gSimulation.kp;
		gHMI.recipe.data.heating.tn := gSimulation.tn;		
	END_IF;

	(* burner *)
	fLCRPT2burner(enable := TRUE, V := 1.0, T1 := 30.0, T2 := 30.0, x := MAX(BOOL_TO_REAL(doBurner) * BURNER_MAX_TEMP * 1.1, SIM_ROOM_TEMP), y_set := SIM_ROOM_TEMP, set := 0);
	gActData.heating.burner.tempAct := fLCRPT2burner.y;
	
	(* boiler *)
	fLCRPT2boiler(enable := TRUE, V := 1.0, T1 := 30.0, T2 := 30.0, x := MAX(BOOL_TO_REAL(doBoilerPump) * gActData.heating.burner.tempAct, SIM_ROOM_TEMP), y_set := SIM_ROOM_TEMP, set := 0);
	gActData.heating.hotwater.tempAct := fLCRPT2boiler.y;
	
	(* heating flow *)
	mixerBurner   := gActData.heating.sActMixer/100;			(* this percentage of water is coming from the burner *)
	mixerBackFlow := (100 - gActData.heating.sActMixer)/100;	(* the rest is coming from water coming back from the radiators *)
	tempBackFlow  := gActData.heating.tempFlowAct - 5.0;		(* water which is coming back is 5° colder *)
	tempBackFlow  := MAX(tempBackFlow, SIM_ROOM_TEMP);			(* limit to room temperature *)
	fLCRPT2flow(enable := TRUE, V := 1.0, T1 := 30.0, T2 := 30.0, x := MAX(((gActData.heating.burner.tempAct * mixerBurner) + (tempBackFlow * mixerBackFlow)), SIM_ROOM_TEMP), y_set := SIM_ROOM_TEMP, set := 0);
	gActData.heating.tempFlowAct := fLCRPT2flow.y;
	
	(* living room temperature *)
	fLCRPT2livingroom(enable := TRUE, V := 1.0, T1 := 60.0, T2 := 60.0, x := MAX(BOOL_TO_REAL(doFlowPump) * gActData.heating.tempFlowAct, SIM_ROOM_TEMP), y_set := SIM_ROOM_TEMP, set := 0);
	gActData.heating.tempLivingroomAct := fLCRPT2livingroom.y;
END_PROGRAM
