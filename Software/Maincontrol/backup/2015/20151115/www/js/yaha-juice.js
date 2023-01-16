/* Yaha-juice | (c) 2015 Werner Paulin */
/* Yaha Javascript User Interface Communication Extension */
/*
1. Posts values of all html tags as CGI.fieldstorage to server: populateCGIdataToWrite() or populateCGIdataToRead
2. The server python script acts as a gateway converts this data to a JSON string and forwards it as UDP telegram
3. The final destination python script forms a dictionary out of the JSON string and applies the data, limits it but also builds up a new dictionary and converts it into a JSON string
4. This dictionary will be sent back to the gateway which passes the JSON string on tot the web client
5. In the web client the JSON string will be converted into a JS object and all values will be applied to the addressed DOM elements
*/



var CyclicReadTagList = []
var CyclicReadTimer
var SuspendCyclicReadCnt = 20			//Necessary to delay start of cyclic read to allow fully loading web page (SVG-icons)

var UpdatedTags = []
var BlurTimer

var WriteTagListQueue = []
var ReadTagListQueue = []

var CgiScriptNamePDI = "/cgi-bin/yaha_webbridge.py"

var PostUpdateUiFunctionObj

function yjSuspendCyclicRead()
{
	console.log("read suspended")
	SuspendCyclicReadCnt = 3
}

//read list is written cyclically automatically
function yjDefineCyclicReadTagList(tagList)
{
	CyclicReadTagList = tagList;
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
	var cgiData = []

	if (WriteTagListQueue.length > 0)
	{
		cgiData = populateCGIdataToWrite(WriteTagListQueue)
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
	console.log("yjCylicRefresh()")
	jQuery.post(CgiScriptNamePDI, cgiData,
	function(jsonDataFromServer,status)
    {
		if (jsonDataFromServer.length == 0) { return; }	//do not initate processing data if no data

		//purge all replies from web server while write is active in order to avoid that last read request are coming while write is already active
		if (SuspendCyclicReadCnt > 0) { console.log("Juice: reply purged"); return; }			
		
		updateUI(jsonDataFromServer)
		if (PostUpdateUiFunctionObj) PostUpdateUiFunctionObj(jsonDataFromServer)
    });
}

//Sends values of DOM tags to server and updates DOM tags according to response of server
function yjWriteTagList(tagList)
{
	yjSuspendCyclicRead()	//suspend cyclic read while writing to give writing priority
	WriteTagListQueue = WriteTagListQueue.concat(tagList)
}

//Sends values of DOM tags to server and updates DOM tags according to response of server
function yjReadTagList(tagList)
{
	ReadTagListQueue = ReadTagListQueue.concat(tagList)
}


function yjOverrideCGIscriptName(newScriptName)
{
	CgiScriptNamePDI = newScriptName;
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




