/* Yaha-hmi | (c) 2015 Werner Paulin */
/* Yaha user interface */
/*
Menu control and user interaction
*/


function showMainNavSelector()
{
	$('#flyinMainNavSelector').show()	
	$('#flyinMainNavSelector').animate({'top':'-25px'},500);
}

function hideMainNavSelector()
{
	$('#flyinMainNavSelector').animate({'top':'-50px'},500,function()
    {
    	$('#flyinMainNavSelector').hide()
    });
}



function showMainNav()
{
	$('#flyinMainNavOverlay').fadeIn('fast',function()
	{
    	$('#flyinMainNav').animate({'top':'-5px'},500);
        $('#flyinMainNav').show()
		hideMainNavSelector()
    });

}

function hideMainNav()
{
	$('#flyinMainNav').animate({'top':'-305px'},500,function()
	{
    	$('#flyinMainNavOverlay').fadeOut('fast');
        $('#flyinMainNav').hide()
    });
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
	//add dynamic style adaption to all yaha icons
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

