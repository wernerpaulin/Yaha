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
var AvailableLanguages = {"en": "English", "de": "Deutsch"};


var FALLBACK_LANGUAGE = "en"
var ActiveLanguage = FALLBACK_LANGUAGE

function onClickMainNav(jQelement)
{
	/* get module id from property of clicked hyperlink */
	moduleTargetId = getYahaProperty(jQelement, "module_target_id")[0];
	
	/* initiated module activation */
	activateModule(moduleTargetId)

	/* close main navigation panel */
	$("#panelMainNav").panel("close");
}

function activateModule(moduleNameID)
{
	//do not request module from server in case of test page
	if (moduleNameID == "$test$")
	{
		//copy test section in active module div which is the base for sub module navigation
		$(".yaha-active-module").html($(".yaha-test-module").html())
		//set name of module as title
		$("#header_text").html("!! Test Module !!")
		//build sub module navigation
		buildSubModuleNavigation()
	}
	else
	{
		//request module from server
		requestModuleContent(moduleNameID, ActiveLanguage)
	}
	
	//keep active module in mind
	ActiveModuleID = moduleNameID;
}



//sends a cgi request to server to get module content
function requestModuleContent(nameID, language)
{
	var cgiData = {}
	
	if (nameID == "")
	{
		nameID = YAHA_DEFAULT_MODULE;
	}
	
	cgiData["requestType"] = "getModuleContent";	
	cgiData["moduleNameID"] = nameID;	
	cgiData["language"] = language;	

	jQuery.post(CgiScriptNameModules, cgiData,
			function(htmlDataFromServer,status)
		    {
				//copy html data in active module div which is the base for sub module navigation
				$(".yaha-active-module").html(htmlDataFromServer)
				//set name of module as title
				$("#header_text").html(ModuleNameList[nameID][MODULE_NAME_INDEX])
				//build sub module navigation
				buildSubModuleNavigation()
		    });
}




//walk through DOM with jQuery as soon as document is fully loaded
jQuery(document).ready(function()
{
	/* read cookies */
	ActiveLanguage = Cookies.get('COOKIE_YAHA_VIEW_LANGUAGE');
	if (ActiveLanguage == undefined)
	{
		ActiveLanguage = FALLBACK_LANGUAGE; 
	}

	/* build main navigation */
	buildMainNavigation(YAHA_DEFAULT_MODULE)
});

//Build main navigtion
function buildMainNavigation(moduleToShow)
{
	var cgiData = {}
	cgiData["requestType"] = "getModuleList";
	cgiData["language"] = ActiveLanguage;	


	jQuery.post(CgiScriptNameModules, cgiData,
				function(jsonDataFromServer,status)
			    {
					//clear current main navigation 
					$("#panelMainNav").empty()

					//data from server comes in JSON format => convert to JavaScript object
					ModuleNameList = jQuery.parseJSON(jsonDataFromServer)
					
					//create new buttons according to list
					var mainNavHtmlString = ""
					mainNavHtmlString += '<div id="main_nav_panel_header"><object data="svg/yaha_logo.svg" type="image/svg+xml" height="80px"></object></div>'
					mainNavHtmlString += '<div id="main_nav_panel_content">'
					
					for (moduleNameID in ModuleNameList)
					{
						//console.log(ModuleNameList[moduleNameID])
						mainNavHtmlString += '<a href="#" data-role="button" data-iconpos="left" data-icon="' + ModuleNameList[moduleNameID][MODULE_ICON_INDEX] + '" class="ui-nodisc-icon" onclick="onClickMainNav($(this))" yaha="module_target_id:' + moduleNameID + '"' + '>' + ModuleNameList[moduleNameID][MODULE_NAME_INDEX] +'</a>'
					}

					//add !! test page !!
					mainNavHtmlString += '<a href="#" data-role="button" data-iconpos="left" data-icon="yaha_debug" class="ui-nodisc-icon" onclick="onClickMainNav($(this))" yaha="module_target_id:$test$">Test</a>'

					mainNavHtmlString += '</div>'
					
					/* Initalize main nav */
					var yahaMainNav = $(mainNavHtmlString).appendTo('#panelMainNav');
					$('#panelMainNav').append(yahaMainNav).trigger('create');	
					
					/* load a default module on request */
					if (moduleToShow) requestModuleContent(moduleToShow, ActiveLanguage)
			    });
}


//Build submodule navigation
//Each navbar element is a void hyperlink with an onclick event handler
//In order to change content, during initialization the ID of the submodul will be transformed into a hyperlink yaha property: submodule_target_id
//The name of the navbar element is derived from the yaha property module_name specified in the submodule
function buildSubModuleNavigation()
{
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
	
	//show one of the sub module which had the visible - onload configured
	$( ".yaha-submodule-active" ).trigger( "click" );
}

function setLanguage(language)
{
	ActiveLanguage = language;
	buildMainNavigation("");	//do not change currently visible sub module - only update main menue
	activateModule(ActiveModuleID)
	Cookies.set('COOKIE_YAHA_VIEW_LANGUAGE', language, { expires: 365 });
}


function updateSubModuleContent(jQelement)
{
	subModuleID = getYahaProperty(jQelement, "submodule_target_id")[0]

	//load content of submodule into page content
	$(".ui-content").html($("#" + subModuleID).html())	

	if ($("#select-language").length)
	{	
		//bind change event to language selector
		$("#select-language").val(ActiveLanguage)
		$("#select-language").change(
				function() 
				{
					setLanguage($(this).find('option:selected').val())
				});	
	
		$("#select-language").blur(
				function() 
				{
					setLanguage($(this).find('option:selected').val())
				});	
	}

	//search for all jQuery widgets (data-role) and refresh them after reloading the content div
	jQueryRefreshWidgetsInContent()
	
	
	
	//Refresh Yaha PDI communication with newly loaded content
	yjAttributeProcessor()
}

function jQueryRefreshWidgetsInContent()
{
	 //find all data-role widgets
	 $(".ui-content [data-role]").each(function() 
	 {
		if ( $(this).attr('data-role') != "button" )	/* do not refresh buttons - strange result */
		{
			try 
			{
				$(this)[$(this).attr('data-role')]();				//this.['collapsible']()
				$(this)[$(this).attr('data-role')]('refresh');		//this.['collapsible']('refresh')
			}
			catch(err) 
			{
				console.log("jQueryRefreshWidgetsInContent(): " + err)
			}
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
			console.log("jQueryRefreshWidgetsInContent(): " + err)
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
}
