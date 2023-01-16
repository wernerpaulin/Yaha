/* Yaha-hmi | (c) 2015 Werner Paulin */
/* Yaha user interface */
/*
Menu control and user interaction
*/

function homepressed()
{
	$("#panelMainNav").panel("close");
}

function getSVGobject(id)
{
	var svgContainer = document.getElementById(id);
	var svgDoc = svgContainer.getSVGDocument();

	return(svgDoc)	
}

function iconOnMouseOver(id)
{
	getSVGobject(id).setStyleHighlight()
}

function iconOnMouseOut(id)
{
	getSVGobject(id).resetStyle()
}

function iconOnClick(id)
{
	getSVGobject(id).setStyleInverted()
}


//walk through DOM with jQuery as soon as document is fully loaded
jQuery(document).ready(function()
{
	//add dynamic style adaptation to all yaha icons
	$(".yahaIcon").each(function() 
	{
		// $(this) contains the tag which surrounds the svg object
		// $(this).find('object').prop('id') is the id of the svg object
		
		//events to surrounding tag: handover ID of svg object
		$(this).click(function(){ iconOnClick($(this).find('object').prop('id')); });
		$(this).mouseover(function(){ iconOnMouseOver($(this).find('object').prop('id')); });
		$(this).mouseout(function(){ iconOnMouseOut($(this).find('object').prop('id')); });
	});



});

