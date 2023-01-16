/* Yaha-view | (c) 2015 Werner Paulin */
/* Yaha view automation */
/*
Menu control and user interaction
*/

var CgiScriptNameModules = "/cgi-bin/yaha_view.py"
var ModuleNameList = {}
var MODULE_ICON_INDEX = 0
var MODULE_NAME_INDEX = 1
var ActiveModuleID = ""
var YAHA_DEFAULT_MODULE = "overview"
var AvailableLanguages = {};
var PDI_CYCLIC_REFRESH_TIME = 300

var FALLBACK_LANGUAGE = "en"
var ActiveLanguage = FALLBACK_LANGUAGE
var ModuleContentList = {}		/* nameID: html string */
var ModuleLoadedCnt = 0
var TEST_MODULE_NAME_ID = "$test$"




//initalize page as soon as document is fully loaded
jQuery(document).ready(function()
{
	/* get language saved from last session */
	ActiveLanguage = getSavedLanguage();
	
	/* get all available languages from server */
	getAvailableLanguages(function(availableLanguages) /* call back function */
			{
				//set global variable
				AvailableLanguages = availableLanguages;
				
				//check if currently active language is one of the available languages
				if (!(ActiveLanguage in AvailableLanguages))
				{
					console.log("Active language set to fall back language")
					ActiveLanguage = FALLBACK_LANGUAGE; 
				}
				
				/* reload all Yaha modules */
				reloadYahaView(ActiveLanguage, function()
						{
							showModuleContent(YAHA_DEFAULT_MODULE)
						}) /* reloadYahaView */
			}) /* getAvailableLanguages */
});	/* jQuery(document).ready */ 


function getSavedLanguage()
{
	/* read cookies */
	return Cookies.get('COOKIE_YAHA_VIEW_LANGUAGE');
}

/* get available languages */
function getAvailableLanguages(callbackFunction)
{
	var cgiData = {}
	cgiData["requestType"] = "getAvailableLanguages";

	jQuery.post(CgiScriptNameModules, cgiData,
		function(jsonDataFromServer,status)
	    {	
			//data from server comes in JSON format => convert to JavaScript object
			var availableLanguages =jQuery.parseJSON(jsonDataFromServer)
			
			callbackFunction(availableLanguages)
	    });	
}

/* get list of all installed Yaha modules */
function getModuleList(language, callbackFunction)
{
	var cgiData = {}
	cgiData["requestType"] = "getModuleList";
	cgiData["language"] = language;	

	jQuery.post(CgiScriptNameModules, cgiData,
				function(jsonDataFromServer,status)
			    {
					//data from server comes in JSON format => convert to JavaScript object
					var moduleNameList = jQuery.parseJSON(jsonDataFromServer)

					//add local test page to module list
					var testModuleEntry = []
					testModuleEntry[MODULE_ICON_INDEX] = 'yaha_debug'
					testModuleEntry[MODULE_NAME_INDEX] = '!! TEST PAGE !!'
					
					moduleNameList[TEST_MODULE_NAME_ID] = testModuleEntry
					
					/* store module names in global list */
					ModuleNameList = moduleNameList;
					/* return to caller */
					callbackFunction(moduleNameList)
			    });
}


function reloadYahaView(activeLanguage, callbackFunction)
{
	$( "#popup_wait" ).popup( "open" )
	getModuleList(activeLanguage, function(moduleNameList)
			{
				/* build main navigation */
				buildMainMenu(moduleNameList)
				
				/* get content of all modules and store them in a text array for fast GUI response */
				//console.log(Object.keys(ModuleNameList).length)
				//moduleNameID = Object.keys(ModuleNameList)[3]
				
				ModuleLoadedCnt = 0
				for (moduleNameID in moduleNameList)
				{
					getModuleContent(moduleNameID, ActiveLanguage, function(moduleNameID, htmlStream)
							{
								ModuleContentList[moduleNameID] = htmlStream	//save html content of module in list for later display

								ModuleLoadedCnt += 1;		//increase counter of number loaded modules to findout when all modules have been loaded
								progress = ModuleLoadedCnt * 100 / Object.keys(moduleNameList).length
								$("#load_progress").html(progress + '%')
								
								if (ModuleLoadedCnt == Object.keys(moduleNameList).length)	//check if all modules have been loaded
								{
									$( "#popup_wait" ).popup( "close" )
									callbackFunction();
								}
							}) /* getModuleContent */
				} /* for (moduleNameID in moduleNameList) */
			}) /* getModuleList */
}


//sends a cgi request to server to get module content
function getModuleContent(nameID, language, callbackFunction)
{
	var cgiData = {}
	
	if (nameID == "")
	{
		return;
	}
	
	//do not request module from server in case of test page
	if (nameID == "$test$")
	{
		//copy test section in active module div which is the base for sub module navigation
		$(".yaha-active-module").html()

		callbackFunction(nameID, $(".yaha-test-module").html())
		return;
	}	
	
	cgiData["requestType"] = "getModuleContent";	
	cgiData["moduleNameID"] = nameID;	
	cgiData["language"] = language;	

	jQuery.post(CgiScriptNameModules, cgiData,
			function(xmlModuleDataFromServer,status)
		    {
				//console.log(xmlModuleDataFromServer)
				//access data stream as xml: entire module will be sent to client in xml syntax including info section and html data
				xmlDoc = $.parseXML(xmlModuleDataFromServer),
				$xmlroot = $(xmlDoc)
				//get id of uploaded module for further referencing in ModuleContentList
				$id = $xmlroot.find( "info>id" );				
				nameID = $id.text()
				//get html data from uploaded module
				$html_data = $xmlroot.find( "html_data" );				
				htmlDataFromServer = $html_data.text()
				//console.log(htmlDataFromServer)
				
				callbackFunction(nameID, htmlDataFromServer)
		    });
}

/* build main menu of navigation panel */
function buildMainMenu(moduleNameList)
{
	//clear current main navigation 
	$("#panelMainNav").empty()
	
	//create new buttons according to list
	var mainNavHtmlString = ""

	//mainNavHtmlString += '<div id="main_nav_panel_header"><span class="yaha-symbol yaha-symbol-logo" style="width: 200px; line-height: 80px;"></span></div>'
	mainNavHtmlString += '<div id="main_nav_panel_content">'
	
	for (moduleNameID in moduleNameList)
	{
		mainNavHtmlString += '<a href="#" data-role="button" data-iconpos="left" data-icon="' + moduleNameList[moduleNameID][MODULE_ICON_INDEX] + '" class="ui-nodisc-icon" onclick="onClickMainMenu($(this))" yaha="module_target_id:' + moduleNameID + '"' + '>' + moduleNameList[moduleNameID][MODULE_NAME_INDEX] +'</a>'
	}

	mainNavHtmlString += '</div>'
	
	/* Initalize main nav */
	var yahaMainNav = $(mainNavHtmlString).appendTo('#panelMainNav');
	$('#panelMainNav').append(yahaMainNav).trigger('create');	
}


function onClickMainMenu(jQelement)
{
	/* get module id from property of clicked hyperlink */
	moduleId = getYahaProperty(jQelement, "module_target_id")[0];
	
	/* initiated module activation */
	showModuleContent(moduleId)

	/* close main navigation panel */
	$("#panelMainNav").panel("close");
}


//show module
function showModuleContent(moduleNameId)
{
	//set name of module as title
	$("#header_text").html(ModuleNameList[moduleNameId][MODULE_NAME_INDEX])

	//copy html stream from content list in to active module for further processing
	$(".yaha-active-module").html(ModuleContentList[moduleNameId])	

	//keep active module in mind
	ActiveModuleID = moduleNameID;
	
	//build sub navigation and show a default sub module
	buildSubMenu()
}



//Build submodule navigation
//Each navbar element is a void hyperlink with an onclick event handler
//In order to change content, during initialization the ID of the submodul will be transformed into a hyperlink yaha property: submodule_target_id
//The name of the navbar element is derived from the yaha property module_name specified in the submodule
function buildSubMenu()
{
	var subModuleIdToShowAfterLoad = ""
	
	//clear current sub module navigation
	$(".ui-footer").empty()
	
	//find all new sub modules and rebuild navigation bar
	var subModuleList = $('.yaha-active-module').find('.yaha-submodule');
	
	/* Build navigation bar - Begin */
	var navbarHtmlString = ""
	navbarHtmlString += '<div data-role="navbar"><ul>'

	/* loop through each sub module and get name for nav bar and ID for content switching */
	subModuleList.each(function() 
	{
		var classYahaSubmoduleActiveString = ""
		try 
		{
			if (getYahaProperty($(this), "visible")[0] == "onload")
			{
				classYahaSubmoduleActiveString = "yaha-submodule-active"
				subModuleIdToShowAfterLoad = $(this).prop("id")
			}
			else
			{
				classYahaSubmoduleActiveString = ""
			}
		}
		catch(err) 
		{
			classYahaSubmoduleActiveString = ""
		}
		
		
		/* template: <li><a href="#" data-icon="yaha_bulb" class="ui-nodisc-icon yaha-submodule-active" onclick="updateSubModuleContent($(this))" yaha="submodule_target_id: yaha_submodule_1">Sub Module 1</a></li> */
		navbarHtmlString += '<li><a href="#" data-icon="' + getYahaProperty($(this), "module_icon")[0] + '" class="ui-nodisc-icon ' + classYahaSubmoduleActiveString + '" onclick="updateSubModuleContent($(this))" yaha="submodule_target_id:' + $(this).prop("id") + '"' + '>' +  getYahaProperty($(this), "module_name")[0] + '</a></li>'
	});

	navbarHtmlString += '</ul></div>'
	/* Build navigation bar - End */

	//Initalize nav bar
	var yahaNavBar = $(navbarHtmlString).appendTo('.ui-footer');
	$('.ui-footer').append(yahaNavBar).trigger('create');	
	
	//show one of the sub module which had the visible - onload flag configured by simulating a click on a button
	$( ".yaha-submodule-active" ).trigger( "click" );
}



//which sub module will be display can either be specified by the call sub menu button (jQuery element) or directly set by a given id (e.g. used after loading a module)
function updateSubModuleContent(jQelement)
{
	yjStopCyclicUIrefresh()	

	subModuleID = getYahaProperty(jQelement, "submodule_target_id")[0]
	
	//load content of submodule into page content
	$(".yaha-ui-content").html($("#" + subModuleID).html())	
	
	//call module specific init script - each module can have a init function
	try 
	{
		moduleInit()
	}
	catch(err) 
	{
		console.log('no moduleInit defined for this module or error in function: ' + err)
	}
	
	//search for all jQuery widgets (data-role) and refresh them after reloading the content div
	jQueryRefreshWidgetsInContent()
	
	//Refresh Yaha PDI communication configuration by reading newly loaded content
	yjAttributeProcessor()
	yjStartCyclicUIrefresh(PDI_CYCLIC_REFRESH_TIME)
}


//finds all interactive elements within a svg and calls a callback function with the id as return value
function yjInitSvgInteraction(idSVG, notificationFunctionObj)
{
	//wait until <object> with svg has been fully loaded
    $('#' + idSVG).on( "load", function(e) 
	{
    	//get calling element which has been finised loading
    	callingElement = e.target
    	//access inner DOM of svg
    	var svgDoc = callingElement.contentDocument; 
        //get the root element of this svg
    	var svgRoot  = svgDoc.documentElement;
        //access via jQuery is now possible using context: svgRoot
   	 	//find all svg elements where class 'yaha-svg-clickable' is set
    	$(".yaha-svg-clickable", svgRoot).each(function() 
   		{
    		//get id of this element
    		elementID = $(this).attr('id')
    		
    		//ignore clickable class if not id is given
    		if (elementID != null)
    		{
       	 		//hook up click event
    			$("#"+elementID, svgRoot).on( "click", function(e) 
   	 			{
    				//notify call which id has been clicked
    				if (notificationFunctionObj != null)
    				{
        				//generic determination of id of calling element
    					notificationFunctionObj(e.target.getAttribute('id'))
    				}
   	 			});     			
    		}
   		});
	});
	
	
}

function jQueryRefreshWidgetsInContent()
{
	 //find all data-role widgets
	 $(".ui-content [data-role]").each(function() 
	 {
		try 
		{
			$(this)[$(this).attr('data-role')]();				//this.['collapsible']()
		}
		catch(err) 
		{
			console.log('jQueryRefreshWidgetsInContent(): data-role ' + $(this).attr('data-role') + err)
		}
	});

	 
	 //special handling for select boxes
	 $(".ui-content select").each(function() 
	 {
		try 
		{
			$(this).selectmenu();
			$(this).selectmenu('refresh');
		}
		catch(err) 
		{
			console.log('jQueryRefreshWidgetsInContent(): select ' + err)
		}
	 });
	 
	 //special handling for input fields
	 $(".ui-content input").each(function() 
	 {
		try 
		{
			/* refresh text inputs, checkboxes have special datarole (e.g. flip-switch) */
			if ($(this).attr('type') == 'text')
			{
				$(this).textinput();
				$(this).textinput('refresh');				
			}
			/* refresh static sliders: dynamically injected sliders use type=number */
			else if ($(this).attr('type') == 'range')
			{
				$(this).textinput();
				$(this).textinput('refresh');	
				$(this).slider();
				$(this).slider('refresh');
			}
			
			/* refresh dynamic sliders: dynamically injected sliders use type=number and data-type=range */
			else if ( ($(this).attr('type') == 'number') && ($(this).attr('data-type') == 'range') )
			{
				$(this).textinput();
				$(this).textinput('refresh');	
				$(this).slider();
				$(this).slider('refresh');
				$(this).hide()	//hide standard display field as it can not be modified in size and position

				//link slider value with span field if requested
				if (getYahaProperty($(this), "mirror_span_id")[0] != "")
				{
					//add change event which updates a linked text field when slider is changed
					$(this).change(function() 	{
													targetID = getYahaProperty($(this), "mirror_span_id")[0]
													$('#'+targetID).html($(this).val());
												});
					
					//update text field immediately
					$(this).change()
				}
			
			}
		}
		catch(err) 
		{
			console.log('jQueryRefreshWidgetsInContent(): input '+ err)
		}
	 });
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

function yvSwitchLanguage(languageID)
{
	ActiveLanguage = languageID;
	yjStopCyclicUIrefresh()	
	reloadYahaView(ActiveLanguage, function()
			{
				Cookies.set('COOKIE_YAHA_VIEW_LANGUAGE', languageID, { expires: 365 });
				console.log(ActiveLanguage)
				showModuleContent(YAHA_DEFAULT_MODULE)
				yjStartCyclicUIrefresh(PDI_CYCLIC_REFRESH_TIME)
			}) /* reloadYahaView */
}
