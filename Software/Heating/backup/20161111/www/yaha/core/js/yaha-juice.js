/* Yaha-juice | (c) 2015 Werner Paulin */
/* Yaha Javascript User Interface Communication Extension */
/*
1. Posts values of all html tags as CGI.fieldstorage to server: populateCGIdataToWrite() or populateCGIdataToRead
2. The server python script acts as a gateway converts this data to a JSON string and forwards it as UDP telegram
3. The final destination python script forms a dictionary out of the JSON string and applies the data, limits it but also builds up a new dictionary and converts it into a JSON string
4. This dictionary will be sent back to the gateway which passes the JSON string on tot the web client
5. In the web client the JSON string will be converted into a JS object and all values will be applied to the addressed DOM elements
*/



var CyclicReadTagList = new Array()
var CyclicReadTimer
var SuspendCyclicReadCnt = 0			//Necessary to delay start of cyclic read to allow fully loading web page (SVG-icons)

var WriteTagListQueue = new Array()
var ReadTagListQueue = new Array()

var CGI_SCRIPT_NAME_YAHA_WEBBRIDGE = "/cgi-bin/yaha_webbridge.py"
var ERROR_RESPONSE_TAG_UNKNOWN = "$unkown$"

var PostUpdateUiFunctionObj

var BlurTimerID = 0
var FormatIDs = {}
var ValueMapIDs = {}

var SymbolMapIDs = {}
var SymbolTargetIDs = {}

var SelectDataIDs = {}
var SelectValueIDs = {}
var SelectValueAutoRefreshIDs = {}

var UnitConversionIDs = {}
var UnitDefinitionTable =	{	"ms" : 0.001 , 					//Table: Unit : relation to base unit (e.g. s)
								"s": 1,
								"min": 60,
								"h" : 3600,
								"day" : 86400,
								"%": 0.01,
								"N": 1,							//N...Number without unit (e.g. for percent conversion)
								"$deg$C": 1,
								"km/h": 1
							}

var AnimationTargetIDs = {}
var AnimationSvgItemIDs = {}
var AnimationAttributes = {}
var AnimationAttributeValueMin = {}
var AnimationAttributeValueMax = {}
var AnimationValueMin = {}
var AnimationValueMax = {}
var VALUE_TYPE_FLOAT = "float"
var VALUE_TYPE_TEXT = "text"


function yjSuspendCyclicRead()
{
	//console.log("read suspended")
	SuspendCyclicReadCnt = 3
}

//read list is written cyclically automatically
function yjDefineCyclicReadTagList(tagList)
{
	CyclicReadTagList = tagList;
	//console.log(CyclicReadTagList)
}

function yjStartCyclicUIrefresh(refreshTime)
{
    CyclicReadTimer = setInterval(function(){ yjCylicRefresh() }, refreshTime);
}

function yjStopCyclicUIrefresh()
{
    clearInterval(CyclicReadTimer);
}

function yjAddPostUpdateUiFunction(f)
{
	PostUpdateUiFunctionObj = f
}

function yjCylicRefresh()
{
	var cgiData = new Array()

	if (WriteTagListQueue.length > 0)
	{
		cgiData = populateCGIdataToWrite(WriteTagListQueue)
		yjSuspendCyclicRead()	//suspend cyclic read while writing to give writing priority

		WriteTagListQueue = []
	}
	else
	{
		//skip this time in case writing is active
		if (SuspendCyclicReadCnt > 0)
		{
			SuspendCyclicReadCnt = SuspendCyclicReadCnt - 1
			return
		}	

		//merge cyclic list to read with individual tags the user might requested in the mean time
		ReadTagListQueue = ReadTagListQueue.concat(CyclicReadTagList);

		cgiData = populateCGIdataToRead(ReadTagListQueue)

		ReadTagListQueue = []
	}

	if (cgiData.length == 0) return;
	
	//send tag list with values to server
	jQuery.post(CGI_SCRIPT_NAME_YAHA_WEBBRIDGE, cgiData,
	function(jsonDataFromServer,status)
    {
		if (jsonDataFromServer.length == 0) { return; }	//do not initiate processing data if no data

		//purge all replies from web server while write is active in order to avoid that last read request are coming while write is already active
		if (SuspendCyclicReadCnt > 0) 
		{ 
			//console.log("Juice: reply purged"); 
			return; 
		}			
		//console.log(jsonDataFromServer)
		updateUI(jsonDataFromServer)
		if (PostUpdateUiFunctionObj) PostUpdateUiFunctionObj(jsonDataFromServer)
    });
}

//adds tags to write to write queue
function yjWriteTagList(tagList)
{
	WriteTagListQueue = WriteTagListQueue.concat(tagList)
}


//Creates an Javascript object which can be passed to the CGI for writing UI data to server: notation: {key: <value>}
function populateCGIdataToWrite(tags)
{
	var dataToServer = {};  //create empty object

	var i = 0;
	
	//loop through all tags which should be transferred to the server
	while (tags[i]) 
	{
		var element = document.getElementById(tags[i]);
		if (typeof(element) != 'undefined' && element != null) //avoid javascript errors
		{ 
			//special handling of input fields
			if (element.nodeName.toLowerCase() == "input")
			{
				//for radio button and checkboxes transfer checked-information rather then the value
				if (element.type == "checkbox")
				{
					if (jQuery("#" + tags[i]).is(":checked") == true)
						dataToServer[tags[i]] = 1
					else
						dataToServer[tags[i]] = 0
				}
				else if (element.type == "radio")
				{
					//see whether a mapping of radio value to a specific PDI exisits. If yes write value to this tag
					if (tags[i] in RadioTargetPDItag)
					{
						dataToServer[RadioTargetPDItag[tags[i]]] = jQuery("#" + tags[i]).val()
					}
					else
					{
						dataToServer[tags[i]] = jQuery("#" + tags[i]).val()
					}
				}
				else
				{
					//for normal text inputs transfer their value
					dataToServer[tags[i]] = jQuery("#" + tags[i]).val()
				}
			}
			//for radio select and textarea transfer their value
			else if ((element.nodeName.toLowerCase() == "select") || (element.nodeName.toLowerCase() == "textarea"))			
			{
				dataToServer[tags[i]] = jQuery("#" + tags[i]).val()
			}
			//for all other tags use text
			else
			{
				dataToServer[tags[i]] = jQuery("#" + tags[i]).text()
			}
		}
		else
		{
			alert("Element '" + tags[i] + "' does not exists on this page")
		}

		i++;
	}	


	return(dataToServer)
}

//Creates an Javascript object which can be passed to the CGI for writing UI data to server: notation: {key: $read$}
function populateCGIdataToRead(tags)
{
	var dataToServer = {};  //create empty object

	var i = 0;
	
	//loop through all tags which should be read from the server
	while (tags[i]) 
	{
		dataToServer[tags[i]] = "$read$"		//indicates that this tag should be read from the server
	    i++;
	}	

	return(dataToServer)
}


function updateUI(jsonData)
{
	//data from server comes in JSON format => convert to JavaScript object
	dataFromServer = jQuery.parseJSON(jsonData)
			
	//apply values from server
	for (tag in dataFromServer)
	{
		//check if tag received from server exists on current website
		var element = document.getElementById(tag);
		
		if (typeof(element) != 'undefined' && element != null) 
		{
			//check if tag did exists on target. If create debugging information
			if (dataFromServer[tag] == ERROR_RESPONSE_TAG_UNKNOWN)
			{
				console.log("Tag unknown on target: " + tag)
				continue
			}
				
			//skip refresh of user interface if element has focus (user is editing) - not for radio and checkboxes otherwise there is not update
			if ((element.type == "radio") || (element.type == "checkbox"))
			{}
			else
			{
				if (tag == document.activeElement.id) continue;
			}

			//write data from server to DOM element
			if (element.nodeName.toLowerCase() == "input")
			{
				//for radio and checkbox elements interpret checked information instead of value
				if ((element.type == "radio") || (element.type == "checkbox"))
				{
					//convert decimal value to binary
					elementValue = (parseFloat(dataFromServer[tag]) == 1.0) ? true : false;
					
					//set element according to value (special handling for jQuery flip switch: needs refresh in order to change
					if (jQuery("#"+tag).attr('data-role') == 'flipswitch')
					{
						jQuery("#"+tag).prop( "checked", elementValue ).flipswitch( "refresh" ) ;
					}
					else
					{
						jQuery("#"+tag).prop("checked", elementValue);
					}
				}
				else
				{
					jQuery("#"+tag).val(dataFromServer[tag]);
				}
			}
			else if ((element.nodeName.toLowerCase() == "select") ||
					 (element.nodeName.toLowerCase() == "textarea"))			
			{
				jQuery("#"+tag).val(dataFromServer[tag]);
			}
			else
			{
				jQuery("#"+tag).text(dataFromServer[tag]);
			}    			
		}
	}	
}

/*
Based on a yaha-specific property certain hmi properties will be defined:
- io_mode: event on which read or/and write will happen: for writing groups can be defined which will be also written in case of an write event
- format: leading zeros, decimal placed
- unit: conversion and display
- value_map: convert number to text (on/off)
- symbol_map: convert number to symbol (icon switching)
- symbol_target_id: specifies the tag id which should be switched
- select: fill select boxes with dynamic (received) data
- anim_target_id: ids of svg graphics which will be animated
- anim_svg_item_id: ids of item in svg graphics whose property should be manipulated
- anim_attributes: names of attributes which should be manipulated
- anim_attr_val_min: lower limit of attribute value
- anim_attr_val_max: upper limit of attribute value
- anim_val_min: lower limit of value (if not given, e.g. for texts, the value will be directly mapped into attribute)
- anim_val_max: upper limit of value (if not given, e.g. for texts, the value will be directly mapped into attribute)
- effect_target_id: specifies the tag id on which the effect should be applied
- effect_type: type of effect for this id
- effect_value_map: which value should cause which effect action 
- radio_map: set radio buttons based on the value of a single variable
- radio_target_pdi_tag: PDI tag which should be written instead of clicked/changed HTML tag
*/
function yjAttributeProcessor()
{
	var readCyclicIDs = new Array()
	var tagGroups = {}

	var writeClickTriggerIDs = {}
	var writeChangeTriggerIDs = {}
	var writeBlurTriggerIDs = {}
	var writeEnterKeyTriggerIDs = {}
	var writeEventTypes = 	{	"click":writeClickTriggerIDs , 
								"change": writeChangeTriggerIDs,
								"blur": writeBlurTriggerIDs,
								"focusout": writeBlurTriggerIDs,			/* focusout might occur as well instead of blur */
								"keypress": writeEnterKeyTriggerIDs
							}
	
	var ATTR_PROPERTY_INDEX = 0
	var ATTR_VALUE_INDEX = 1
	var propertyName = ""
	var propertyValueList = new Array()
	
	FormatIDs = {}
	UnitConversionIDs = {}
	ValueMapIDs = {}
	SymbolMapIDs = {}
	SymbolTargetIDs = {}

	SelectDataIDs = {}
	SelectValueIDs = {}
	SelectValueAutoRefreshIDs = {}	
	AnimationTargetIDs = {}
	AnimationSvgItemIDs = {}
	AnimationAttributes = {}
	AnimationAttributeValueMin = {}
	AnimationAttributeValueMax = {}
	AnimationValueMin = {}
	AnimationValueMax = {}
	
	EffectTargetIDs = {}
	EffectTypes = {}
	EffectValueMap = {}

	RadioMapIDs = {}
	RadioTargetPDItag = {}
	
	
	/* generically write value of a certain input element on enter and remove focus to allow refresh again */
	$("input").attr("autocomplete","off");  //disable auto complete as a single enter might not be sufficient to apply a new value if the value has been entered before
	
	 //find all tags with a yaha attribute - BEGIN
	 $("[yaha]").each(function() 
	 {
		attrString = $(this).attr('yaha');				//property:value1,value2;property:value

		//get all property and values of attribute
		yahaPropertyList = attrString.split(';')
	 	
	 	//analyze properties - BEGIN
	 	for (p in yahaPropertyList) 	//go through each definition: property:value1,value2
	 	{
	 		yahaPropertyEntry = yahaPropertyList[p].trim().split(':')								//remove white space
	 		propertyName = yahaPropertyEntry[ATTR_PROPERTY_INDEX].trim()	//remove white space

			//one property might has more then one value  (e.g. io_mode:read_cyclic,write_click)
			yahaPropertyEntry[ATTR_VALUE_INDEX] = yahaPropertyEntry[ATTR_VALUE_INDEX].trim()		//remove white space
	 		propertyValueList = yahaPropertyEntry[ATTR_VALUE_INDEX].split(',')
			for (pv in propertyValueList) { propertyValueList[pv] = propertyValueList[pv].trim() }	//remove white space for each value
			
			switch(propertyName)
			{
				//io_mode: defines whether the tag will be written or read
				case "io_mode":
					for (pv in propertyValueList)
					{
						switch(propertyValueList[pv])
						{
							case "read_cyclic":
								readCyclicIDs.push($(this).prop('id'))
							break;

							case "write_click":
								if ( ($(this).prop('id') in writeClickTriggerIDs) == false )
								{
									writeClickTriggerIDs[$(this).prop('id')] = ""		//add ID to write list if not yet defined with tag group definition. However group to write will be assigned later on
								}
							break;
							case "write_change":
								if ( ($(this).prop('id') in writeClickTriggerIDs) == false )
								{
									writeChangeTriggerIDs[$(this).prop('id')] = ""		//add ID to write list if not yet defined with tag group definition. However group to write will be assigned later on
								}
							break;
							case "write_blur":
							case "focusout":
								if ( ($(this).prop('id') in writeBlurTriggerIDs) == false )
								{
									writeBlurTriggerIDs[$(this).prop('id')] = ""		//add ID to write list if not yet defined with tag group definition. However group to write will be assigned later on
								}
							break;
							case "write_enter":
								if ( ($(this).prop('id') in writeEnterKeyTriggerIDs) == false )
								{
									writeEnterKeyTriggerIDs[$(this).prop('id')] = ""	//add ID to write list if not yet defined with tag group definition. However group to write will be assigned later on
								}
							break;
							default:
								console.log("yaha-juice::yjAttributeProcessor() - unknown property value: " + propertyValueList[pv])
						}
					}	
				break;

				//tag_group_wr_click: defines which tag group should be written in case a click event on this ID has been fired 
				case "tag_group_wr_click":
					writeClickTriggerIDs[$(this).prop('id')] = propertyValueList[0]		//add name of tag group which should be written
				break;

				//tag_group_wr_change: defines which tag group should be written in case a change event on this ID has been fired 
				case "tag_group_wr_change":
					writeChangeTriggerIDs[$(this).prop('id')] = propertyValueList[0]		//add name of tag group which should be written
				break;
				
				//tag_group_wr_blur: defines which tag group should be written in case a blur event on this ID has been fired 
				case "tag_group_wr_blur":
					writeBlurTriggerIDs[$(this).prop('id')] = propertyValueList[0]		//add name of tag group which should be written
				break;
				
				//tag_group_wr_enter: defines which tag group should be written in case the enter key will be pressed on this ID has been fired 
				case "tag_group_wr_enter":
					writeEnterKeyTriggerIDs[$(this).prop('id')] = propertyValueList[0]	//add name of tag group which should be written
				break;
				
				//tag_group: one tag can be member of several groups. All members of a group will be treated the same way (e.g. for writing)
				case "tag_group":
					for (pv in propertyValueList)							
					{
						if (propertyValueList[pv] in tagGroups)
						{
							//group with ID array exists already -> add new ID
							tagGroups[propertyValueList[pv]].push($(this).prop('id'))	//group name: [ID1, ID2,...]
						}
						else
						{
							//groups has not yet been created -> create group, initialize it as array and add new ID
							tagGroups[propertyValueList[pv]] = []
							tagGroups[propertyValueList[pv]].push($(this).prop('id'))
						}
					}
				break;
				case "format":
					FormatIDs[$(this).prop('id')] = propertyValueList[0]			//add format string of tag which should be applied when received from server
				break;
				case "unit":
					UnitConversionIDs[$(this).prop('id')] = propertyValueList[0]	//add unit conversion string of tag which will be interpreted on update
				break;
				case "value_map":
					ValueMapIDs[$(this).prop('id')] = propertyValueList				//add value mapping of tag which should be applied when received from server
				break;
				case "symbol_map":
					SymbolMapIDs[$(this).prop('id')] = propertyValueList			//add symbol mapping of tag which should be applied when received from server
				break;
				case "symbol_target_id":
					SymbolTargetIDs[$(this).prop('id')] = propertyValueList			//add id of tag which should be switched by symbol mapping
				break;
				case "select_data":
					SelectDataIDs[propertyValueList[0]] = $(this).prop('id')		//add ID of element which will contain data to populate select box
				break;
				case "select_value":
					SelectValueIDs[$(this).prop('id')] = propertyValueList[0]		//add ID of element which will contain the value which is show by the select box
					SelectValueAutoRefreshIDs[$(this).prop('id')] = true			//per default the value which is displayed in a select box will be refreshed after initialization
					
					/* automatic refresh of value stops as soon as */
					$(this).focusin(function() 
							{
								SelectValueAutoRefreshIDs[$(this).prop('id')] = false	//stop automatic refresh of displayed value as soon as the user manipulate the select box
							})
				break;
				case "anim_target_id":
					AnimationTargetIDs[$(this).prop('id')] = propertyValueList			//add ids of svg graphics which will be animated
				break;
				case "anim_svg_item_id":
					AnimationSvgItemIDs[$(this).prop('id')] = propertyValueList			//add ids of item in svg graphics whose property should be manipulated
				break;
				case "anim_attribute":
					AnimationAttributes[$(this).prop('id')] = propertyValueList			//add names of attributes which should be manipulated
				break;
				case "anim_attr_val_min":
					AnimationAttributeValueMin[$(this).prop('id')] = propertyValueList	//add lower limit of attribute value
				break;
				case "anim_attr_val_max":
					AnimationAttributeValueMax[$(this).prop('id')] = propertyValueList	//add upper limit of attribute value
				break;
				case "anim_val_min":
					AnimationValueMin[$(this).prop('id')] = propertyValueList			//add lower limit of value (if not given, e.g. for texts, the value will be directly mapped into attribute)
				break;
				case "anim_val_max":
					AnimationValueMax[$(this).prop('id')] = propertyValueList			//add upper limit of value (if not given, e.g. for texts, the value will be directly mapped into attribute)
				break;
				case "effect_target_id":
					EffectTargetIDs[$(this).prop('id')] = propertyValueList				//add ids of tags which on which an effect should be applied
				break;
				case "effect_type":
					EffectTypes[$(this).prop('id')] = propertyValueList				//add ids of tags which on which an effect should be applied
				break;
				case "effect_value_map":
					EffectValueMap[$(this).prop('id')] = propertyValueList				//add effect action mapping of tag which should be applied when received from server
				break;
				case "radio_map":
					RadioMapIDs[$(this).prop('id')] = propertyValueList				//add radio ID mapping of tag which should be set checked when received from server
				break;
				case "radio_target_pdi_tag":
					RadioTargetPDItag[$(this).prop('id')] = propertyValueList				//add target PDI tag should be set when a radio tag has been clicked or changed
				break;
			}			
		}
	 	//analyze properties - END
	 });	
	//find all tags with a yaha attribute - END
	 
	//Initialize all tags which has been configured for cyclic read
	yjDefineCyclicReadTagList(readCyclicIDs)
	
	//go through each supported event types and dynamically add all event handlers for each ID of each type
	for (eventType in writeEventTypes)
	{
		//Hook all IDs which should be written on click event
		for (id in writeEventTypes[eventType])		//e.g. writeClickTriggerIDs
		{
			$(document).on(eventType, "#" + id, 	//eventType = click, blur,...
			function(event)
			{
				//console.log(event)
				//Special extension in case of enter key pressed
				if (event.type == "keypress")
				{
				  var keycode = (event.keyCode ? event.keyCode : event.which);	//compatibility: use event.which if keyCode does not exists
				  if(keycode == '13')	//enter key
				  {
					//delay blur otherwise applying value to element won't work stable
					BlurTimerID = setInterval(function(){ clearInterval(BlurTimerID); $("#" + document.activeElement.id).blur()}, 100);	//in case timer is elapsed, stop it and blur currently focused (active) element
				  }
				  else
				  {
					  //in case of any other key do not continue initiating any write commands		
					  return
				  }
				}

				//writeEventTypes[event.type][id] contains tag group to write
				if (writeEventTypes[event.type][$(this).prop('id')] == "")							//no group specified -> send id of tag
				{
					yjWriteTagList(new Array($(this).prop('id')));
				}
				else
				{
					yjWriteTagList(tagGroups[writeEventTypes[event.type][$(this).prop('id')]])		//group specified -> send members of group (if ID of trigger tag not in group then it will not be sent)
				}
			});			
		}		
	}

	//hook post processing function into update cycle so formating of numbers and units is possible
	yjAddPostUpdateUiFunction(postUpdateUi)
}

//this function can be used to reformat raw valued from the server
function postUpdateUi(jsonData)
{
	//data from server comes in JSON format => convert to JavaScript object
	dataFromServer = jQuery.parseJSON(jsonData)

	//update only tags which where updated
	for (tag in dataFromServer)
	{
		numFloat = parseFloat(jQuery("#"+ tag).text())
		
		//VALUE MAP: check if for this tag a value mapping has been defined
		if (tag in ValueMapIDs)
		{
			//loop through all value maps and see which one fits. Stop loop after mapping has been applied
			for (map in ValueMapIDs[tag])					//1=on, 0=off
			{
				mapping = ValueMapIDs[tag][map].split("=")	//1=on
				if (mapping[0] == numFloat)					//index 0 contains value
				{
					jQuery("#"+ tag).text(mapping[1])		//index 1 contains replacement value or text
					break;
				}
			}
		}
				
		//SYMBOL MAP: check if for this tag a value mapping has been defined
		if (tag in SymbolMapIDs)
		{
			//loop through all value maps and see which one fits. Stop loop after mapping has been applied
			for (map in SymbolMapIDs[tag])					//1=on, 0=off
			{
				mapping = SymbolMapIDs[tag][map].split("=")	//1=icon_name
				if (mapping[0] == numFloat)					//index 0 contains value
				{
					//check if target ID is given => if not abort symbol mapping
					if (SymbolTargetIDs[tag] == "")
					{
						console.log("SymbolTargetIDs not defined for tag: " + tag)
						break;
					}
					
					jQuery("#" + SymbolTargetIDs[tag]).removeClass()
					jQuery("#" + SymbolTargetIDs[tag]).addClass("yaha-symbol")
					jQuery("#" + SymbolTargetIDs[tag]).addClass(mapping[1])
					break;
				}
			}
		}
		
		
		
		//UNITS: check if for this tag a unit conversion has been defined
		showUnit = false
		srcUnit = ""
		dstUnit = ""	

		if (tag in UnitConversionIDs)
		{
			unitSyntax = UnitConversionIDs[tag].split(" ")
			//go through all unit properties
			for (unitProperty in unitSyntax)
			{
				switch(unitSyntax[unitProperty])
				{
					case "show":
						showUnit = true			//unit will be added once all numerical operations have been finished 
					break;
					default:
						//watch out for conversion definition: syntax is like: "s>ms show"
						if (unitSyntax[unitProperty].indexOf(">") > 0)
						{
							srcUnit = unitSyntax[unitProperty].split(">")[0]	
							dstUnit = unitSyntax[unitProperty].split(">")[1]
						}
					break;
				}
			}

			//get number for html
			numFloat = parseFloat(jQuery("#"+ tag).text())

			//do unit conversion only if source and destination untis have been given
			if (srcUnit != "" && dstUnit != "")
			{
				//check for devision by zero
				try 
				{
					numFloat = numFloat * UnitDefinitionTable[srcUnit] / UnitDefinitionTable[dstUnit]
				}
				catch(err) 
				{
				    console.log(err.message)
				}

				//get string of converted float value				
				jQuery("#"+ tag).text(numFloat.toString())
			}
			else
			{
				jQuery("#"+ tag).text(numFloat.toString())
			}

		}
		
		//FORMATING: check if for this tag a special formating rule has been defined
		if (tag in FormatIDs)
		{
			//format like: 00.##, .##
			if (FormatIDs[tag].split(".").length > 1)
			{
				//get of leading zeros
				nbLeadingZeros = FormatIDs[tag].split(".")[0].replace(/[^0]/g, "").length  //trick: use reg-exp to remove all characters except "0" and then count the length of the remaining string

				//get number of decimal places
				nbDecimalPlaces = FormatIDs[tag].split(".")[1].length
			}
			//format like 00
			else
			{
				//get of leading zeros
				nbLeadingZeros = FormatIDs[tag].replace(/[^0]/g, "").length  //trick: use reg-exp to remove all characters except "0" and then count the length of the remaining string
				
				//assume no decimal places
				nbDecimalPlaces = 0
			}

			
			//apply format: decimal places
			numFloat = parseFloat(jQuery("#"+ tag).text())				//convert html text to float
			jQuery("#"+ tag).text(numFloat.toFixed(nbDecimalPlaces))	//trim decimal places and write number as text back to ID
			
			//apply format: leading zeros
			floatString = jQuery("#"+ tag).text()						//keep original float string
			intValue = parseInt(floatString)							//get integer part
			nbDigits = intValue.toString().length						//determine number of integer digits
			isNegative = (intValue < 0 ? true : false)					//find out whether number is negative
			nbDigits = (isNegative == true ? nbDigits - 1 : nbDigits)	//if negative, correct number of digits as "-" has been counted
			zerosToFill = ((nbLeadingZeros - nbDigits) > 0 ? (nbLeadingZeros - nbDigits) : 0)				//if nbDigits more than leading zeros than they are no leading zeros

			floatStringWithLeadingZeros = ""
			for (i=0 ; i < zerosToFill ; i++)
			{
				floatStringWithLeadingZeros = floatStringWithLeadingZeros.concat("0")
			}
			floatStringWithLeadingZeros = floatStringWithLeadingZeros.concat(floatString)
			jQuery("#"+ tag).text(floatStringWithLeadingZeros)
		}
			
		//UNIT DISPLAY: concat unit if configured to show
		if (showUnit == true)
		{
			if (dstUnit == "$deg$C")
			{
				jQuery("#"+ tag).text(jQuery("#"+ tag).text().concat(" " + "\u00B0" + "C"))
			}
			else
			{
				jQuery("#"+ tag).text(jQuery("#"+ tag).text().concat(" " + dstUnit))
			}
		}
		
		//SELECT: check whether list with data to fill select box has been received
		if (tag in SelectDataIDs)		
		{
			try	//fillSelect would fail if tag does not exist anymore due to page change
			{
				if (SelectDataIDs[tag] in SelectValueIDs)
				{
					fillSelect(tag, SelectDataIDs[tag], SelectValueIDs[SelectDataIDs[tag]], SelectValueAutoRefreshIDs[SelectDataIDs[tag]])	//tag contains select data; SelectDataIDs[] contains the id of the select box, SelectValueIDs[] contains the item which should be displayed, SelectValueAutoRefreshIDs[] contains information whether the value should be updated or not
				}
				else
				{
					fillSelect(tag, SelectDataIDs[tag], null, null)	//tag contains select data; SelectDataIDs[tag] contains the id of the select box
					
				}
			}
			catch(err) 
			{
				console.log(tag + ":" + err.message)
			}
		}

		
		//ANIMATION: animate svg graphics based on tag value
		if (tag in AnimationTargetIDs)		//check whether this tag should perform an animation on a svg object
		{
			try	//abort animation if parameters are wrong
			{
				//access inner DOM of svg graphic
				var svgDoc = document.getElementById(AnimationTargetIDs[tag]).contentDocument
						
				//get value from html tag depending on its kind
				if ($("#"+ tag).is("input"))
				{
					animationValue = jQuery("#"+ tag).val()
					animationValueType = VALUE_TYPE_FLOAT
				}
				else
				{
					//can be either text or value
					try				//assume its a value
					{
						animationValue = parseFloat(jQuery("#"+ tag).text())
						animationValueType = VALUE_TYPE_FLOAT
					}
					catch(err)		//assume it is a text (e.g for color animation)
					{
						animationValue = jQuery("#"+ tag).text()
						animationValueType = VALUE_TYPE_TEXT
					}
				}

				//in case of a number scale value accordingly to fit to animation range of svg item attribute
				if (animationValueType == VALUE_TYPE_FLOAT)
				{
					//x = animationValue
					//x1 = AnimationValueMin[tag]
					//x2 = AnimationValueMax[tag]
					//y1 = AnimationAttributeValueMin[tag]
					//y2 = AnimationAttributeValueMax[tag]
					//y = attributeValue	
					var k = calcK(parseFloat(AnimationValueMin[tag]), parseFloat(AnimationAttributeValueMin[tag]), parseFloat(AnimationValueMax[tag]), parseFloat(AnimationAttributeValueMax[tag]))
					var d = calcD(parseFloat(AnimationValueMin[tag]), parseFloat(AnimationAttributeValueMin[tag]), parseFloat(AnimationValueMax[tag]), parseFloat(AnimationAttributeValueMax[tag]))
					
					//calulate attribute value by linar interpolation
					attributeValue = calcY(k, d, animationValue, AnimationAttributeValueMin[tag], AnimationAttributeValueMax[tag])
				}
				else
				{
					attributeValue = animationValue	//dont modify the value
				}

				//special interpretation of transform attribute: transform.rotate,...
				if (AnimationAttributes[tag][0] == "transform")
				{
					if (AnimationAttributes[tag][1] == "rotate")
					{
						attributeValue = 360 - attributeValue
						//access specific item within in SVG and modify a certain attribute: change svg rotation to clockwise rotation angle		
						svgDoc.getElementById(AnimationSvgItemIDs[tag]).setAttribute("transform", "rotate(" + attributeValue + ")");
					}
				}
				else
				{
					//access specific item within in SVG and modify a certain attribute		
					svgDoc.getElementById(AnimationSvgItemIDs[tag][0]).setAttribute(AnimationAttributes[tag], attributeValue);
				}

			}
			catch(err) 
			{
				console.log(tag + ":" + err.message)
			}
			
		}

		//EFFECT: apply effect to an ID
		if (tag in EffectTargetIDs)		
		{
			try	//abort effect if parameters are wrong
			{
				switch(EffectTypes[tag][0])
				{
					case "visibility":
						//loop through all value maps and see which one fits received value
						for (map in EffectValueMap[tag])					//0=hide, 1=show
						{
							mapping = EffectValueMap[tag][map].split("=")	//0=hide
							if (mapping[0] == numFloat)						//index 0 contains value
							{
								if (mapping[1] == "show")
								{
									jQuery("#"+ EffectTargetIDs[tag]).show()
									break;
								}
								else if  (mapping[1] == "hide")
								{
									jQuery("#"+ EffectTargetIDs[tag]).hide()
									break;
								}
							}
						}						
						
					break;
					default:
						console.log("yaha-juice::yjAttributeProcessor() - unknown effect type: " + EffectTypes[tag][0])
						
				}

				
			}
			catch(err) 
			{
				console.log(tag + ":" + err.message)
			}
		}
		
		//RADIO button: set radio button depending on value of ID
		if (tag in RadioMapIDs)	
		{
			try	//abort effect if parameters are wrong
			{
				//loop through all value maps and see which one fits received value
				for (map in RadioMapIDs[tag])						//0=ID1, 1=ID2
				{
					mapping = RadioMapIDs[tag][map].split("=")		//0=ID1
					if (mapping[0] == numFloat)						//index 0 contains value
					{
						jQuery("#"+ mapping[1]).prop("checked", true).checkboxradio("refresh");;
					}
					//reset all other radio button IDs which do not match the received value
					else
					{
						jQuery("#"+ mapping[1]).prop("checked", false).checkboxradio("refresh");;
					}
				}
			}
			catch(err) 
			{
				console.log(tag + ":" + err.message)
			}
		}
			
	} //for (tag in dataFromServer)
	
}

function calcK(x1, y1, x2, y2)
{
	try	//catch division be zero and others
	{
		return( (y2 -y1) / (x2 - x1) )
	}
	catch(err) 
	{
		console.log("yaha-juice::calcK():" + err.message)
		return(0)
	}	
}

function calcD(x1, y1, x2, y2)
{
	try	//catch division be zero and others
	{
		return( ((y1 * x2) - (y2 * x1)) / (x2 - x1) )
	}
	catch(err) 
	{
		console.log("yaha-juice::calcD():" + err.message)
		return(0)
	}	
}

function calcY(k, d, x, yMin, yMax)
{
	//y = kx + d
	y = k * x + d
			
	//limit calculated value
	if (y > yMax) y = yMax
	if (y < yMin) y = yMin

	return( y )
}


function fillSelect(idSelectListJSON, idSelect, idSelectValue, autoRefresh)
{
	var selectList = jQuery.parseJSON(jQuery("#"+ idSelectListJSON).text()) //convert recipe list back to a list object
	var sel = document.getElementById(idSelect);
	var selectValue = ""									

	if ( (idSelectValue != null) && (autoRefresh == true) )
	{
		selectValue = $("#"+idSelectValue).text()			//use value of a certain html tag to define which option should be displayed
	}
	else
	{
		selectValue = $("#"+idSelect).val()					//no html tag id which contains the value which should be display given -> remember currently selected recipe
	}


	$("#"+idSelect).empty();									//remove all items before adding new			

	//build up selector list
	for(var i = 0; i < selectList.length; i++) 
	{
	    var opt = document.createElement('option');
	    opt.innerHTML = selectList[i];
	    opt.value = selectList[i];
	    sel.appendChild(opt);
	}				
	
	$("#"+idSelect).val(selectValue)						//set selector back to selected recipe name (if exists)
	$("#"+idSelect).selectmenu();
	$("#"+idSelect).selectmenu('refresh');
}

function getYahaProperty(jQelement, propertyNameToFind)
{
	var ATTR_PROPERTY_INDEX = 0
	var ATTR_VALUE_INDEX = 1
	var propertyName = ""
	var propertyValueList = new Array()

	//get yaha attribute information from clicked element 
	attrString = jQelement.attr('yaha')
	//check whether there is a yaha attribute given
	if ((attrString) == "") return propertyValueList;
	
	//get all property and values of attribute
	yahaPropertyList = attrString.split(';')
	
 	//analyze properties - BEGIN
 	for (p in yahaPropertyList) 	//go through each definition: property:value1,value2
 	{
 		yahaPropertyEntry = yahaPropertyList[p].trim().split(':')								//remove white space
 		propertyName = yahaPropertyEntry[ATTR_PROPERTY_INDEX].trim()	//remove white space

 		//look for specific property name
 		if (propertyName != propertyNameToFind) continue;
 		
		//one property might has more then one value  (e.g. io_mode:read_cyclic,write_click)
		yahaPropertyEntry[ATTR_VALUE_INDEX] = yahaPropertyEntry[ATTR_VALUE_INDEX].trim()		//remove white space
 		propertyValueList = yahaPropertyEntry[ATTR_VALUE_INDEX].split(',')
		for (pv in propertyValueList) { propertyValueList[pv] = propertyValueList[pv].trim() }	//remove white space for each value
		
		return propertyValueList;
 	}
	//analyze properties - END

	//at this position it seems the requested property could not be found -> return an empty array
	propertyValueList = [];
	return propertyValueList;
}


/*
http://www.sitepoint.com/testing-for-empty-values/
undefined or null
a zero-length string
an array with no members
an object with no enumerable properties
*/
function empty(data)
{
  if(typeof(data) == 'number' || typeof(data) == 'boolean')
  { 
    return false; 
  }
  if(typeof(data) == 'undefined' || data === null)
  {
    return true; 
  }
  if(typeof(data.length) != 'undefined')
  {
    return data.length == 0;
  }
  var count = 0;
  for(var i in data)
  {
    if(data.hasOwnProperty(i))
    {
      count ++;
    }
  }
  return count == 0;
}


