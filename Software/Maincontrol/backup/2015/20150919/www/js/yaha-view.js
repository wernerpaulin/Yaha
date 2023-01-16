/* Yaha-hmi | (c) 2015 Werner Paulin */
/* Yaha user interface */
/*
Menu control and user interaction
*/

var MAIN_NAV_SLIDE_DURATION = 200
var CONTENT_OVERLAY_OPACITY = 0.5

function showMainNavHandle()
{
	$('#slideOverMainNav_handle').show()
	$('#slideOverMainNav_content').css({"box-shadow": "0 0 20px 5px #808080"})
	$('#slideOverMainNav_content').css({"-webkit-box-shadow": "0 0 20px 5px #808080"})
}

function hideMainNavHandle()
{
    $('#slideOverMainNav_handle').hide()
	$('#slideOverMainNav_content').css({"box-shadow": "none"})
	$('#slideOverMainNav_content').css({"-webkit-box-shadow": "none"})
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

	
	$('#contentOverlay').click(function(){hideMainNav();} );

	
	//add main navigation handle animation
	$('#slideOverMainNav_handleArea').mouseover(function(){showMainNavHandle();} );
	//additional handlers for touch devices
	$('#slideOverMainNav_handleArea').click(function(){showMainNavHandle();} );
	$('#content_container').click(function(){hideMainNavHandle();} );
	//reactivate dragging if it has been disabled
	$('#slideOverMainNav_container').mouseover(function(){$('#slideOverMainNav_container').draggable("enable");} );
	
	
	$(function() 
	{
	    $( "#slideOverMainNav_container" ).draggable({
	    	axis: "y", 
	    	scroll: false,

	    	//Initialize variables
	        start: function(event, ui) {
	            this.previousPosition = ui.position;
	            this.direction = 'stop'
	        },
	    	
	    	// Drag current position of dragged image.
	        drag: function(event, ui) {
	            // get current position of object
	            var currentPos = $(this).position();
	            
	            //detect direction of dragging
	            this.direction = (this.previousPosition.top > ui.position.top) ? 'up' : 'down'
	            this.previousPosition = ui.position;
	            
	            //fade overlay depending on dragged position
	            fadeOverlay("contentOverlay", -currentPos.top, 0, $(this).height(), CONTENT_OVERLAY_OPACITY)
	            
	            //Limit dragging area
	            if (this.direction == 'down')
	            {
		            if (currentPos.top >= 0)
		            {
		            	ui.position = {'top': 0, 'left':currentPos.left};
		            	$(this).draggable("disable")
		            }	
	            }
	        },
	        
	    

	    	// Continue sliding depending on what the user intended to do
	        stop: function(event, ui) {
	        	var currentPos = $(this).position();
	            
	            if (this.direction == 'down')
	            {
		        	if (currentPos.top >= ($(this).height() - $(this).height()/4) * -1)
		            {
		        		$(this).animate({'top':'0'},
				        				{duration: MAIN_NAV_SLIDE_DURATION, step: function( currentTop, fx)
				        										{	//fade overlay depending on dragged position
						        			            			fadeOverlay("contentOverlay", -currentTop, 0, $(this).height(), CONTENT_OVERLAY_OPACITY);
				        										},
				        				});
		            }
		        	else
		        	{
		        		$(this).animate({'top':'-560'},
				        				{duration: MAIN_NAV_SLIDE_DURATION, step: function( currentTop, fx )
				        										{	//fade overlay depending on dragged position
						        			            			fadeOverlay("contentOverlay", -currentTop, 0, $(this).height(), CONTENT_OVERLAY_OPACITY);
				        										},
						        						complete: function(){	$('#contentOverlay').hide(); 
						        												hideMainNavHandle();
						        											}
				        				});
		        	}
	            }
	            else
	            {
		        	if (currentPos.top <= - $(this).height()/4)
		            {
		        		$(this).animate({'top':'-560'},
		        						{duration: MAIN_NAV_SLIDE_DURATION, step: function( currentTop, fx )
				        										{	//fade overlay depending on dragged position
				        											fadeOverlay("contentOverlay", -currentTop, 0, $(this).height(), CONTENT_OVERLAY_OPACITY);
				        										},
								        				complete: function(){	$('#contentOverlay').hide(); 
								        										hideMainNavHandle();
								        									}
				        				});
		            }
		        	else
		        	{
		        		$(this).animate({'top':'0'},
		        						{duration: MAIN_NAV_SLIDE_DURATION, step: function( currentTop, fx)
		        												{	//fade overlay depending on dragged position
		        													fadeOverlay("contentOverlay", -currentTop, 0, $(this).height(), CONTENT_OVERLAY_OPACITY);
		        												}
		        						});
		        	}	            	
	            }
	            

	        }
	    
	    });
	    
	 });


	$(function(){
		  $("#pieChart").drawPieChart([
		    { title: "Tokyo",         value : 180,  color: "#02B3E7" },
		    { title: "San Francisco", value:  60,   color: "#CFD3D6" },
		    { title: "London",        value : 50,   color: "#736D79" },
		    { title: "New York",      value:  30,   color: "#776068" },
		    { title: "Sydney",        value : 20,   color: "#EB0D42" },
		    { title: "Berlin",        value : 20,   color: "#FFEC62" },
		    { title: "Osaka",         value : 7,    color: "#04374E" }
		  ]);
		});
});

//fade overlay depending on dragged position
function fadeOverlay(id, currentPos, minPos, maxPos, minOpacity)
{	
	var opacity = minOpacity/(maxPos - minPos) * (maxPos - currentPos)
	opacity = Math.min(Math.max(opacity, 0),1)

	$("#" + id).fadeTo(0, opacity);
}



//jQuery - add ons /Begin
//Swipe up/down (courtesy: http://jsfiddle.net/Q3d9H/1/)
//add multi touch gestures
//jquery_addon_swipe_up_down()
//$('#content_container').on('swipedown',function(){showMainNav();} );
//$('#content_container').on('swipeup',function(){hideMainNav();} );
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
