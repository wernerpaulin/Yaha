(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: ENGINEERING.SIGNAL_PROCESSING
*)
(*@KEY@:DESCRIPTION*)
version 1.0	19. may. 2008
programmer 	oscat
tested BY	oscat

SEL2_OF_3B is used to connect 3 binary sensors to one signal. the output Q reflects the state of at least two inputs.
if two or more of the 3 inputs ate TRUE then Q will be TRUE and if two or more of the three inputs are FALSE then Q will be false.
the main putrpose is the connection of 3 redundant binary sensors.  
The output W will be active when one of the 3 inputs is of different state.
to avoid flickering while the sensors are switching the output W will become active after a programmed delay of TD.
(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK SEL2_OF_3B

(*Group:Default*)


VAR_INPUT
	IN1 :	BOOL;
	IN2 :	BOOL;
	IN3 :	BOOL;
	TD :	TIME;
END_VAR


VAR_OUTPUT
	Q :	BOOL;
	W :	BOOL;
END_VAR


VAR
	TDEL :	TON;
END_VAR


(*@KEY@: WORKSHEET
NAME: SEL2_OF_3B
IEC_LANGUAGE: ST
*)
Q := (IN1 AND IN2) OR (IN1 AND IN3) OR (IN2 AND IN3);
TDEL(IN := (in1 XOR in2) OR (in1 XOR in3) OR (in2 XOR in3), PT := TD);
W := TDEL.Q;

(* revision history
hm		19. may 2008	rev 1.0
	original version

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
