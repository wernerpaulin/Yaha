(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: MATHEMATICAL.MATHE
*)
(*@KEY@:DESCRIPTION*)
version 1.9	10. mar. 2009
programmer 	hugo
tested by	tobias

this function calculates a pseudo random number
to generate the number it reads the sps timer and calculates a random number between 0 and 1:
in order to use rdm more then once within one sps cycle it need to be called with different seed numbers LAST.

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK RDM

(*Group:Default*)


VAR_INPUT
	LAST :	REAL;
END_VAR


VAR_OUTPUT
	RDM :	REAL;
END_VAR


VAR
	T_PLC_MS :	T_PLC_MS;
	tn :	DWORD;
	tc :	INT;
END_VAR


(*@KEY@: WORKSHEET
NAME: RDM
IEC_LANGUAGE: ST
*)
T_PLC_MS();
tn := UDINT_TO_DWORD(T_PLC_MS.T_PLC_MS);
tc := Bit_Count(tn);

tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,2),31); (* tn.31 := tn.2; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,5),30); (* tn.30 := tn.5; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,4),29); (* tn.29 := tn.4; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,1),28); (* tn.28 := tn.1; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,0),27); (* tn.27 := tn.0; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,7),26); (* tn.26 := tn.7; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,6),25); (* tn.25 := tn.6; *)
tn:=BIT_LOAD_DW(tn,BIT_OF_DWORD(tn,3),24); (* tn.24 := tn.3; *)

tn := ROL(tn,Bit_Count(tn)) OR DWORD#16#80000001;
tn := UDINT_TO_DWORD(DWORD_TO_UDINT(tn) MOD UDINT#71474513 + _INT_TO_UDINT(tc) + UDINT#77);
RDM := fract(_DWORD_TO_REAL(tn) / 10000000.0 * (2.71828182845904523536028747135266249 - LIMIT_REAL(0.0,last,1.0)));


(*
pt := ADR(temp);
pt^ := (T_PLC_MS() AND 16#007FFFFF) OR 16#3D000000;
RDM := fract(modR(temp*e+pi1, PI1-last) + modR(temp*PI1+e + last,e-last));
*)

(* revision history
hm		16. jan 2007		rev 1.0
	original version

hm		11. nov 2007		rev 1.1
	changed time() into t_plc_ms()

hm		20. nov 2007		rev 1.2
	changed code of temp calculation to avoid overflow in modr due to resuclt would not fit DINT for high timeer values

hm		5. jan 2008		rev 1.3
	changed calculation of temp to avoid problem with high values of t_plc_ms

hm		2. feb 2008		rev 1.4
	changed algorithm to avoind non iec functions and guarantee more randomness

hm	10. mar. 2008		rev 1.5
	make sure last will be between 0 and 1 to avoid invalid results

hm	16. mar. 2008		rev 1.6
	added conversion for tc to avoid warnings under codesys 3.0

hm	18. may. 2008		rev 1.7
	changed constant E to E1

hm	18. oct. 2008		rev 1.8
	using math constants

hm	10. mar. 2009		rev 1.9
	real constants updated to new systax using dot

*)
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
