/* Yaha-view | (c) 2015 Werner Paulin */
/* Yaha view automation */
/*
Menu control and user interaction
*/

var CGI_SCRIPT_NAME_YAHA_VIEW = "/cgi-bin/yaha_view.py"
var ModuleNameList = {}
var MODULE_ICON_INDEX = 0
var MODULE_NAME_INDEX = 1
var YAHA_DEFAULT_MODULE = "overview"
var AvailableLanguages = {};			
var PDI_CYCLIC_REFRESH_TIME = 200

var FALLBACK_LANGUAGE = "en"			/* set by cookie */
var ActiveLanguage = FALLBACK_LANGUAGE

var ModuleContentList = {}				/* nameID: html string */
var ModuleLoadedCnt = 0

var ModuleViewOrder = []				/* set by cookie */
		
//initalize page as soon as document is fully loaded
jQuery(document).ready(function()
{
	/* get language saved from last session */
	ActiveLanguage = yvReadCookieLanguage();
	
	ModuleViewOrder = yvReadCookieModuleViewOrder()

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
					yvWriteCookieLanguage(ActiveLanguage)
				}
				
				/* reload all Yaha modules */
				reloadYahaModules(ActiveLanguage, function()
						{
							showModuleContent(YAHA_DEFAULT_MODULE)
						}) /* reloadYahaModules */
			}) /* getAvailableLanguages */
			
	$(document).on("click", "#pageheader",
			function(event)
			{
				$("#panelMainNav").panel("open");
			});			
	
	
});	/* jQuery(document).ready */ 



function yvWriteCookieModuleViewOrder(moduleViewOrder)
{
	var moduleViewOrderString = ""

	for (i = 0; i < moduleViewOrder.length; i++)
	{
		//insert comma after the first element to separate them
		if (i > 0) { moduleViewOrderString = moduleViewOrderString.concat(',') }
		//add moduleNameID to string
		moduleViewOrderString = moduleViewOrderString.concat(moduleViewOrder[i])
	}
		
	Cookies.set('COOKIE_YAHA_VIEW_MODULE_VIEW_ORDER', moduleViewOrderString, { expires: 365 });  
}

function yvReadCookieModuleViewOrder()
{
	moduleViewOrderString = Cookies.get('COOKIE_YAHA_VIEW_MODULE_VIEW_ORDER')

	if (moduleViewOrderString != null)
	{
		/* write back cookie imediately to refresh expire date */
		Cookies.set('COOKIE_YAHA_VIEW_MODULE_VIEW_ORDER', moduleViewOrderString, { expires: 365 }); 
		
		/* convert string to array and return it */
		return moduleViewOrderString.split(',');
	}
	else
	{
		moduleViewOrderString = []				//no cookies yet set --> return an empty array
		return moduleViewOrderString;
	}
}

function yvWriteCookieLanguage(languageID)
{
	Cookies.set('COOKIE_YAHA_VIEW_LANGUAGE', languageID, { expires: 365 });  
}


function yvReadCookieLanguage()
{
	/* read cookies */
	languageID = Cookies.get('COOKIE_YAHA_VIEW_LANGUAGE')
	
	/* write back cookie imediately to refresh expire date */
	Cookies.set('COOKIE_YAHA_VIEW_LANGUAGE', languageID, { expires: 365 });
	
	return languageID;
}

/* get available languages */
function getAvailableLanguages(callbackFunction)
{
	var cgiData = {}
	cgiData["requestType"] = "getAvailableLanguages";

	jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
		function(jsonDataFromServer,status)
	    {	
			//data from server comes in JSON format => convert to JavaScript object
			var availableLanguages =jQuery.parseJSON(jsonDataFromServer)
			
			callbackFunction(availableLanguages)
	    });	
}

function reloadYahaModules(activeLanguage, callbackFunction)
{
	$( "#popup_wait" ).popup( "open" )

	getModuleList(activeLanguage, function(moduleNameList)
			{
				/* store module names in global list */
				ModuleNameList = moduleNameList;

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
								progress = progress.toFixed(0)	//show no decimal places
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


/* get list of all installed Yaha modules */
function getModuleList(language, callbackFunction)
{
	var cgiData = {}
	cgiData["requestType"] = "getModuleList";
	cgiData["language"] = language;	

	jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
				function(jsonDataFromServer,status)
			    {
					//data from server comes in JSON format => convert to JavaScript object
					var moduleNameList = jQuery.parseJSON(jsonDataFromServer)

					/* return to caller */
					callbackFunction(moduleNameList)
			    });
}


//sends a cgi request to server to get module content
function getModuleContent(nameID, language, callbackFunction)
{
	var cgiData = {}
	
	if (nameID == "") { return; }
	
	cgiData["requestType"] = "getModuleContent";	
	cgiData["moduleNameID"] = nameID;	
	cgiData["language"] = language;	

	jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
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
	var newModuleViewOrder = []

	//clear current main navigation 
	$("#panelMainNav").empty()
	
	//create new buttons according to list
	var mainNavHtmlString = ""

	//mainNavHtmlString += '<div id="main_nav_panel_header"><span class="yaha-symbol yaha-symbol-logo" style="width: 200px; line-height: 80px;"></span></div>'
	mainNavHtmlString += '<div id="main_nav_panel_content">'

	//1. add modules to main navigation according to defined order 
	for (i = 0; i < ModuleViewOrder.length; i++)
	{
		moduleNameID = ModuleViewOrder[i]
				
		/* Add only modules from order list which also exists on target */ 
		if (moduleNameID in moduleNameList)
		{
			iconName = moduleNameList[moduleNameID][MODULE_ICON_INDEX]
			moduleName = moduleNameList[moduleNameID][MODULE_NAME_INDEX]
					
			mainNavHtmlString += '<a href="#" data-role="button" data-iconpos="left" data-icon="' + iconName + '" class="ui-nodisc-icon" onclick="onClickMainMenu($(this))" yaha="module_target_id:' + moduleNameID + '"' + '>' + moduleName +'</a>'
			newModuleViewOrder.push(moduleNameID)		//build new order list based on modules which really exists
		}
	}	
	
	//2. add remaining modules on target in case of dynamically added all modules which are not yet defined in the order list 
	for (moduleNameID in moduleNameList)
	{
		/* Skip modules which have been already added to main navigation because they were listed in order list */ 
		if ( $.inArray(moduleNameID, ModuleViewOrder) >= 0 ) { continue; }
		
		mainNavHtmlString += '<a href="#" data-role="button" data-iconpos="left" data-icon="' + moduleNameList[moduleNameID][MODULE_ICON_INDEX] + '" class="ui-nodisc-icon" onclick="onClickMainMenu($(this))" yaha="module_target_id:' + moduleNameID + '"' + '>' + moduleNameList[moduleNameID][MODULE_NAME_INDEX] +'</a>'
		
		newModuleViewOrder.push(moduleNameID)		//add also new modules which are on the target but where not yet listed in the order list
	}

	mainNavHtmlString += '</div>'
	
	//3. update public module view order list with the newly ordered list
	ModuleViewOrder = newModuleViewOrder
	yvWriteCookieModuleViewOrder(ModuleViewOrder)

	/* Initalize main navigation */
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
	yjStopCyclicUIrefresh()	

	//set name of module as title
	$("#header_text").html(ModuleNameList[moduleNameId][MODULE_NAME_INDEX])

	
	//purge current content
	$(".yaha-ui-content").empty()

	//nullify an old init function loaded into the browser cache from a previous module 
	moduleInit = undefined

	//load content of submodule into page content
	$(".yaha-ui-content").html(ModuleContentList[moduleNameId])	
	
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
	var subModuleList = $('.yaha-ui-content').find('.yaha-submodule');
	
	/* Build navigation bar - Begin */
	var navbarHtmlString = ""
	navbarHtmlString += '<div data-role="navbar"><ul>'

	/* loop through each sub module and get name for nav bar and ID for content switching */
	subModuleList.each(function() 
	{
		//hide all sub modules as default
		$(this).hide()
		
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
		
		
		/* template: <li><a href="#" data-icon="yaha_bulb" class="ui-nodisc-icon yaha-submodule-active" onclick="showSubModuleContent($(this))" yaha="submodule_target_id: yaha_submodule_1">Sub Module 1</a></li> */
		navbarHtmlString += '<li><a href="#" data-icon="' + getYahaProperty($(this), "module_icon")[0] + '" class="ui-nodisc-icon ' + classYahaSubmoduleActiveString + '" onclick="showSubModuleContent($(this))" yaha="submodule_target_id:' + $(this).prop("id") + '"' + '>' +  getYahaProperty($(this), "module_name")[0] + '</a></li>'
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
function showSubModuleContent(jQelement)
{
	subModuleID = getYahaProperty(jQelement, "submodule_target_id")[0]

	//get list of all submodules
	var subModuleList = $('.yaha-ui-content').find('.yaha-submodule');	

	/* loop through each sub module show only the one which  */
	subModuleList.each(function() 
	{
		if ($(this).prop("id") == subModuleID)
		{
			$(this).show()
		}
		else
		{
			$(this).hide()
		}
	});
}


//finds all interactive elements within a svg and calls a callback function with the id as return value
function yvInitSvgInteraction(idSVG, notificationFunctionObj)
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



function yvSwitchLanguage(languageID)
{
	ActiveLanguage = languageID;
	yjStopCyclicUIrefresh()	

	//check if currently active language is one of the available languages
	if (!(ActiveLanguage in AvailableLanguages))
	{
		ActiveLanguage = FALLBACK_LANGUAGE;
	}	

	//save newly selected language as cookie
	yvWriteCookieLanguage(ActiveLanguage)
	reloadYahaModules(ActiveLanguage, function()
			{
				console.log("Language: modules loaded: " + ActiveLanguage)

				showModuleContent(YAHA_DEFAULT_MODULE)
				yjStartCyclicUIrefresh(PDI_CYCLIC_REFRESH_TIME)
			}) /* reloadYahaModules */
}

function yvUpdateMainNavigation()
{
	buildMainMenu(ModuleNameList)
}


