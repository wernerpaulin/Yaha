(*@PROPERTIES_EX@
TYPE: POU
LOCALE: 0
IEC_LANGUAGE: ST
PLC_TYPE: independent
PROC_TYPE: independent
GROUP: SETUP
*)
(*@KEY@:DESCRIPTION*)

(*@KEY@:END_DESCRIPTION*)
FUNCTION_BLOCK SETUP_CHARNAMES

(*Group:Default*)


VAR_IN_OUT
	CHARNAMES :	oscat_CHARNAMES;
END_VAR


VAR
	init :	BOOL;
END_VAR


(*@KEY@: WORKSHEET
NAME: SETUP_CHARNAMES
IEC_LANGUAGE: ST
*)
(* Daten initialisieren *)
IF init THEN RETURN; END_IF;

init := TRUE;

CHARNAMES[01] := ';"&quot;&&amp;<&lt;>&gt;?&euro;?&nbsp;?&iexcl;?&cent;?&pound;?&curren;?&yen;';
CHARNAMES[02] := ';?&brvbar;?&sect;?&uml;?&copy;?&ordf;?&laquo;?&not;?&shy;?&reg;?&macr;?&deg;';
CHARNAMES[03] := ';?&plusmn;?&sup2;?&sup3;?&acute;?&micro;?&para;?&middot;?&cedil;?&sup1;?&ordm;';
CHARNAMES[04] := ';?&raquo;?&frac14;?&frac12;?&frac34;?&iquest;?&Agrave;?&Aacute;?&Acirc;?&Atilde;';
CHARNAMES[05] := ';?&Auml;?&Aring;?&AElig;?&Ccedil;?&Egrave;?&Eacute;?&Ecirc;?&Euml;?&Igrave;';
CHARNAMES[06] := ';?&Iacute;?&Icirc;?&Iuml;?&ETH;?&Ntilde;?&Ograve;?&Oacute;?&Ocirc;?&Otilde;';
CHARNAMES[07] := ';?&Ouml;?&times;?&Oslash;?&Ugrave;?&Uacute;?&Ucirc;?&Uuml;?&Yacute;?&THORN;';
CHARNAMES[08] := ';?&szlig;?&agrave;?&aacute;?&acirc;?&atilde;?&auml;?&aring;?&aelig;?&ccedil;';
CHARNAMES[09] := ';?&egrave;?&eacute;?&ecirc;?&euml;?&igrave;?&iacute;?&icirc;?&iuml;?&eth;';
CHARNAMES[10] := ';?&ntilde;?&ograve;?&oacute;?&ocirc;?&otilde;?&ouml;?&divide;?&oslash;?&ugrave;';
CHARNAMES[11] := ';?&uacute;?&ucirc;?&uuml;?&yacute;?&thorn;?&yuml;';
(*@KEY@: END_WORKSHEET *)
END_FUNCTION_BLOCK
