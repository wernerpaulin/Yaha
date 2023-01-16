/*! Yaha-juice | (c) 2015 Werner Paulin */
/* Yaha Javascript User Interface communication Extension */
/*
1. Post values of all html tags as CGI.fieldstorage to server: populateCGIdataToWrite() or populateCGIdataToRead
2. The server python script acts as a gateway converts this data to a JSON string and forwards it as UDP telegram
3. The final destination python script forms a dictionary out of the JSON string and applies the data, limits it but also builds up a new dictionary and converts it into a JSON string
4. This dictionary will be sent back to the gateway which passes the JSON string on tot the web client
5. In the web client the JSON string will be converted into a JS object and all values will be applied to the addressed DOM elements
*/



var CyclicReadTagList = []
var CyclicReadTimer
var SuspendCyclicRefreshCnt = 0
var UpdatedTags = []


var WriteOnEnterTagList = []
var WriteOnEnterTrigger

var CgiScriptName = "/cgi-bin/yaha_webbridge.py"

var PostUpdateUiFunctionObj

function yjSuspendReadingWhileWriting()
{
	SuspendCyclicRefreshCnt = 3
}

//list list is written cyclically automatically
function yjDefineCyclicReadTagList(tagList)
{
	CyclicReadTagList = tagList;
}

//this list is written when the enter key has been pressed
function yjDefineWriteOnEnterTagList(tagList)
{
	WriteOnEnterTagList = tagList;
}

function yjStartCyclicUIrefresh(refreshTime)
{
    var CyclicReadTimer = setInterval(function(){ yjReadTagList(CyclicReadTagList) }, refreshTime);
}

function yjStopCyclicUIrefresh()
{
    clearInterval(CyclicReadTimer);
}

function yjAddPostUpdateUiFunction(f)
{
	PostUpdateUiFunctionObj = f
}

//Sends values of DOM tags to server and updates DOM tags according to response of server
function yjWriteTagList(tagList)
{
	//suspend reading while write is active
	yjSuspendReadingWhileWriting()
	
	//send tag list with values to server
	jQuery.post(CgiScriptName, populateCGIdataToWrite(tagList),
    //process replied data from server (server checks permission, limits values and replies the resulting data for immediate update)
	function(jsonDataFromServer,status)
    {
		updateUI(jsonDataFromServer)
		if (PostUpdateUiFunctionObj) PostUpdateUiFunctionObj(jsonDataFromServer)
    });
}

//Sends values of DOM tags to server and updates DOM tags according to response of server
function yjReadTagList(tagList)
{
	//skip this time in case writing is active
	if (SuspendCyclicRefreshCnt > 0)
	{
		SuspendCyclicRefreshCnt = SuspendCyclicRefreshCnt - 1
		return
	}

	//send tag list with values to server
	jQuery.post(CgiScriptName, populateCGIdataToRead(tagList),
    //process replied data from server (server checks permission, limits values and replies the resulting data for immediate update)
	function(jsonDataFromServer,status)
    {
		//just in case a write has been initiated a bit before write() did the suspend, prevent user interface from updating to avoid flickering of display
		if (SuspendCyclicRefreshCnt > 0) return

		updateUI(jsonDataFromServer)
		if (PostUpdateUiFunctionObj) PostUpdateUiFunctionObj(jsonDataFromServer)
    });
}


function yjOverrideCGIscriptName(newScriptName)
{
	CgiScriptName = newScriptName;
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
				if ((element.type == "radio") || (element.type == "checkbox"))
				{
					if (jQuery("#" + tags[i]).is(":checked") == true)
						dataToServer[tags[i]] = 1
					else
						dataToServer[tags[i]] = 0
				}
				else
				{
					//for normal text inputs transfer their value
					dataToServer[tags[i]] = jQuery("#" + tags[i]).val()
				}
			}
			//for select and textarea transfer their value
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
					if (parseFloat(dataFromServer[tag]) == 1.0)
					{
						jQuery("#"+tag).prop("checked", true);
					}
					else
					{
						jQuery("#"+tag).prop("checked", false);
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

/* write values on enter and remove focus to allow refresh again */
$(document).keypress(function(event)
{
  var keycode = (event.keyCode ? event.keyCode : event.which);
  if(keycode == '13')	//enter key
  {
    yjWriteTagList(WriteOnEnterTagList);
    document.getElementById(document.activeElement.id).blur();
  }
});


function addCommas(nStr)
{
	nStr += '';
	x = nStr.split('.');
	x1 = x[0];
	x2 = x.length > 1 ? '.' + x[1] : '';
	var rgx = /(\d+)(\d{3})/;
	while (rgx.test(x1)) {
		x1 = x1.replace(rgx, '$1' + ',' + '$2');
	}
	return x1 + x2;
}

