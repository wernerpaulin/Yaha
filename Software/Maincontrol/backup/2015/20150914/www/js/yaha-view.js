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
	$('#contentOverlay').fadeIn('fast',function()
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
    	$('#contentOverlay').fadeOut('fast');
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

	jquery_addon_swipe_up_down()
	
	//add multi touch gestures
	$('#content_container').on('swipedown',function(){showMainNav();} );
	$('#content_container').on('swipeup',function(){hideMainNav();} );
});




//jQuery - add ons /Begin
//Swipe up/down (courtesy: http://jsfiddle.net/Q3d9H/1/)
function jquery_addon_swipe_up_down()
{
	var supportTouch = $.support.touch,
									scrollEvent = "touchmove scroll",
									touchStartEvent = supportTouch ? "touchstart" : "mousedown",
									touchStopEvent = supportTouch ? "touchend" : "mouseup",
									touchMoveEvent = supportTouch ? "touchmove" : "mousemove";

	$.event.special.swipeupdown = {
        setup: function() {
            var thisObject = this;
            var $this = $(thisObject);
            $this.bind(touchStartEvent, function(event) {
                var data = event.originalEvent.touches ?
                        event.originalEvent.touches[ 0 ] :
                        event,
                        start = {
                            time: (new Date).getTime(),
                            coords: [ data.pageX, data.pageY ],
                            origin: $(event.target)
                        },
                        stop;

                function moveHandler(event) {
                    if (!start) {
                        return;
                    }
                    var data = event.originalEvent.touches ?
                            event.originalEvent.touches[ 0 ] :
                            event;
                    stop = {
                        time: (new Date).getTime(),
                        coords: [ data.pageX, data.pageY ]
                    };

                    // prevent scrolling
                    if (Math.abs(start.coords[1] - stop.coords[1]) > 10) {
                        event.preventDefault();
                    }
                }
                $this
                        .bind(touchMoveEvent, moveHandler)
                        .one(touchStopEvent, function(event) {
                    $this.unbind(touchMoveEvent, moveHandler);
                    if (start && stop) {
                        if (stop.time - start.time < 1000 &&
                                Math.abs(start.coords[1] - stop.coords[1]) > 30 &&
                                Math.abs(start.coords[0] - stop.coords[0]) < 75) {
                            start.origin
                                    .trigger("swipeupdown")
                                    .trigger(start.coords[1] > stop.coords[1] ? "swipeup" : "swipedown");
                        }
                    }
                    start = stop = undefined;
                });
            });
        }
    };
    $.each({
        swipedown: "swipeupdown",
        swipeup: "swipeupdown"
    }, function(event, sourceEvent){
        $.event.special[event] = {
            setup: function(){
                $(this).bind(sourceEvent, $.noop);
            }
        };
    });
}
//jQuery - add ons /End
