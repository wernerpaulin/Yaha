/**
 * @name		jQuery KnobKnob plugin
 * @author		Martin Angelov
 * @version 	1.0
 * @url			http://tutorialzine.com/2011/11/pretty-switches-css3-jquery/
 * @license		MIT License
 */

/* 	HTML code:
	<div class="knobBarContainer" id="floorHeatingReducedTempBars" >
		<div class="knobWheelContainer" id="floorHeatingReducedTempKnob"></div>
	</div>	

	Script:
	call knobWidgetInit() with onload()
 */

function knobWidgetInit(idKnob, idBars, snapToZeroValue, startValue, minValue, maxValue, stepWidthValue, minDegree, maxDegree, barSpacingDegrees, valueTagId)
{
	var rad2deg = 180/Math.PI;
	var deg = 0;
	var bars = $('#'+idBars);

	//x = value
	//x1 = minValue
	//x2 = maxValue
	//y1 = minDegree
	//y2 = maxDegree
	//y = degree	
	var d = calcD(minValue, minDegree, maxValue, maxDegree)
	var k = calcK(minValue, minDegree, maxValue, maxDegree)

	var startDegree = calcY(k, d, startValue, minDegree, maxDegree)
	var snapToZeroDegree = calcY(k, d, snapToZeroValue, minDegree, maxDegree)
	
	var nbBars = (maxDegree - minDegree) / barSpacingDegrees
	
	for(var i=0;i<nbBars;i++)
	{
		//index bar
		deg = i * barSpacingDegrees
		
		// Create the colorbars
		$('<div class="colorBar">').css({
			backgroundColor: getColorBlueToRed(i/nbBars),
			transform:'rotate('+deg+'deg)',
			top: -Math.sin(deg/rad2deg)*80+100,
			left: Math.cos((180 - deg)/rad2deg)*80+100,
		}).appendTo(bars);
	}
	
	var colorBars = bars.find('.colorBar');
	var numBars = 0, lastNum = -1;
	
	$('#'+idKnob).knobKnob({
		snap : snapToZeroValue,
		degree: startDegree,
		minDegree: minDegree,
		maxDegree: maxDegree,
		minValue: minValue,
		maxValue: maxValue,
		valueTagId:valueTagId,
		stepWidthValue: stepWidthValue,
		turn : function(ratio, turnByTouchMove){
			//update connected tag variable with new value
			writeTagValue(valueTagId, valueRound(calcX(k, d, ratio * 360, minValue, maxValue), stepWidthValue), turnByTouchMove)

			//ratio: 0..0° 1..360°
			numBars = Math.round(colorBars.length * ratio * 360/(maxDegree - minDegree));
			// Update the dom only when the number of active bars
			// changes, instead of on every move
			if(numBars == lastNum){
				return false;
			}
			lastNum = numBars;
			
			colorBars.removeClass('active').slice(0, numBars).addClass('active');
		}
	});
	
}; 


function getColorBlueToRed(percentage)
{
	return(percentageToHsl(percentage, 225, 360, 280, 50))
}

//https://jsfiddle.net/r438s65s/
function percentageToHsl(percentage, hue0, hue1, hueMaskStart, hueMaskRange) 
{
	//http://www.workwithcolor.com/hsl-color-picker-01.htm
	//red: 0
	//green: 120
	//yellow: 45
	//blue: 225

	var hue = (percentage * (hue1 - hue0)) + hue0;
	//mask a certain range of hue values (e.g. to skip pink between blue and red)
	if (hue >= hueMaskStart) hue = hue + hueMaskRange
    return 'hsl(' + hue + ', 100%, 50%)';
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
		console.log("knobWidget::calcD():" + err.message)
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

function calcX(k, d, y, xMin, xMax)
{
	//y = kx + d
	try
	{
		x = (y - d) / k
	}
	catch(err)
	{
		console.log("knobWidget::calcX():" + err.message)
		return(0)
	}	
	
	//limit calculated value
	if (x > xMax) x = xMax
	if (x < xMin) x = xMin

	return( x )
}



function writeTagValue(id, value, triggerChangeEvent)
{
	try
	{
		//check if tag received from server exists on current website
		var element = document.getElementById(id);

		if (typeof(element) != 'undefined' && element != null) 
		{
			if (element.nodeName.toLowerCase() == "input")
			{
				jQuery("#"+id).val(value);
			}
			else
			{
				jQuery("#"+id).text(value);
			}  

			if (triggerChangeEvent == true)
			{
				//fire change event
				jQuery("#"+id).trigger("change");
			}
			
		}
	}
	catch(err) 
	{
		console.log(id + ":" + err.message)
	}
}

function readTagValue(id)
{
	try
	{
		//check if tag received from server exists on current website
		var element = document.getElementById(id);

		if (typeof(element) != 'undefined' && element != null) 
		{
			if (element.nodeName.toLowerCase() == "input")
			{
				return(jQuery("#"+id).val());
			}
			else
			{
				return(jQuery("#"+id).text());
			}  
		}
	}
	catch(err) 
	{
		console.log(id + ":" + err.message)
	}
}

function valueRound(value, step) {
    step || (step = 1.0);
    var inv = 1.0 / step;
    return Math.round(value * inv) / inv;
}

(function($){
	
	$.fn.knobKnob = function(props){
	
		var options = $.extend({
			snap: 0,
			degree: 0,
			minDegree: 0,
			maxDegree: 360,
			minValue: 0,
			maxValue: 360,
			valueTagId: "",
			stepWidthValue: 1.0,			
			turn: function(){}
		}, props || {});
	
		var tpl = '<div class="knob">\
				<div class="top"></div>\
				<div class="base"></div>\
			</div>';
	
		return this.each(function(){
			
			var el = $(this);
			el.append(tpl);
			
			var knob = $('.knob',el),
				knobTop = knob.find('.top'),
				startDeg = -1,
				currentDeg = 0,
				rotation = 0,
				lastDeg = 0,
				doc = $(document);
			
			if(options.degree > 0 && options.degree <= 359){
				rotation = currentDeg = options.degree;
				turnKnob(knob, currentDeg, options.minDegree, options.maxDegree, options.turn, true)
			}
			
			knob.on('mousedown touchstart', function(e){
			
				e.preventDefault();
			
				var offset = knob.offset();
				var center = {
					y : offset.top + knob.height()/2,
					x: offset.left + knob.width()/2
				};
				
				var a, b, deg, tmp,
					rad2deg = 180/Math.PI;

				//when touch movement starts set focus to connected input field (only works if input field has a tabindex="0") 
				$('#'+options.valueTagId).focus()
				
				knob.on('mousemove.rem touchmove.rem',function(e){
					$('#'+options.valueTagId).focus()

					e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
					
					a = center.y - e.pageY;
					b = center.x - e.pageX;
					deg = Math.atan2(a,b)*rad2deg;
					
					// we have to make sure that negative
					// angles are turned into positive:
					if(deg<0){
						deg = 360 + deg;
					}
					
					// Save the starting position of the drag
					if(startDeg == -1){
						startDeg = deg;
					}
					
					// Calculating the current rotation
					tmp = Math.floor((deg-startDeg) + rotation);
					
					// Making sure the current rotation
					// stays between 0 and 359
					if(tmp < 0){
						tmp = 360 + tmp;
					}
					else if(tmp > 359){
						tmp = tmp % 360;
					}
					
					// Snapping in the off position:
					if(options.snap && tmp < options.snap){
						tmp = 0;
					}
					
					// This would suggest we are at an end position;
					// we need to block further rotation.
					if(Math.abs(tmp - lastDeg) > 180){
						return false;
					}
					
					// Limit turning angle
					currentDeg = Math.max(Math.min(tmp, options.maxDegree), options.minDegree)
					//turn knob
					lastDeg = turnKnob(knob, currentDeg, options.minDegree, options.maxDegree, options.turn, false)
				});
			
				doc.on('mouseup.rem  touchend.rem',function(){
					knob.off('.rem');
					doc.off('.rem');
					
					// Saving the current rotation
					rotation = currentDeg;
					
					// Marking the starting degree as invalid
					startDeg = -1;
					lastDeg = turnKnob(knob, currentDeg, options.minDegree, options.maxDegree, options.turn, true)
				});
			
			});
			
			//hook in change event handler on input field so the knob turns when input field has been changed
			$('#'+options.valueTagId).on('change', function(){
				//scale input value to degree
				//x = value
				//x1 = minValue
				//x2 = maxValue
				//y1 = minDegree
				//y2 = maxDegree
				//y = degree	
				var d = calcD(options.minValue, options.minDegree, options.maxValue, options.maxDegree)
				var k = calcK(options.minValue, options.minDegree, options.maxValue, options.maxDegree)

				var newDeg = calcY(k, d, readTagValue(options.valueTagId), options.minDegree, options.maxDegree)				
				
				rotation = lastDeg = turnKnob(knob, newDeg, options.minDegree, options.maxDegree, options.turn, false)
			});
			
		});
	};
	
})(jQuery);


function turnKnob(knobObj, degree, minDegree, maxDegree, callBack, turnByTouchMove)
{
	try
	{
		knobTopObj = knobObj.find('.top')
		// Limit turning angle
		degree = Math.max(Math.min(degree, maxDegree), minDegree)
		//turn knob
		knobTopObj.css('transform','rotate('+(degree)+'deg)');
		//call callback function
		callBack(degree/359, turnByTouchMove)
		
		return(degree)
	}
	catch(err) 
	{
		console.log("turnKnob():" + err.message)
	}
}

/*
 * transform: A jQuery cssHooks adding cross-browser 2d transform capabilities to $.fn.css() and $.fn.animate()
 *
 * limitations:
 * - requires jQuery 1.4.3+
 * - Should you use the *translate* property, then your elements need to be absolutely positionned in a relatively positionned wrapper **or it will fail in IE678**.
 * - transformOrigin is not accessible
 *
 * latest version and complete README available on Github:
 * https://github.com/louisremi/jquery.transform.js
 *
 * Copyright 2011 @louis_remi
 * Licensed under the MIT license.
 *
 * This saved you an hour of work?
 * Send me music http://www.amazon.co.uk/wishlist/HNTU0468LQON
 *
 */
(function( $ ) {

/*
 * Feature tests and global variables
 */
var div = document.createElement('div'),
	divStyle = div.style,
	propertyName = 'transform',
	suffix = 'Transform',
	testProperties = [
		'O' + suffix,
		'ms' + suffix,
		'Webkit' + suffix,
		'Moz' + suffix,
		// prefix-less property
		propertyName
	],
	i = testProperties.length,
	supportProperty,
	supportMatrixFilter,
	propertyHook,
	propertyGet,
	rMatrix = /Matrix([^)]*)/;

// test different vendor prefixes of this property
while ( i-- ) {
	if ( testProperties[i] in divStyle ) {
		$.support[propertyName] = supportProperty = testProperties[i];
		continue;
	}
}
// IE678 alternative
if ( !supportProperty ) {
	$.support.matrixFilter = supportMatrixFilter = divStyle.filter === '';
}
// prevent IE memory leak
div = divStyle = null;

// px isn't the default unit of this property
$.cssNumber[propertyName] = true;

/*
 * fn.css() hooks
 */
if ( supportProperty && supportProperty != propertyName ) {
	// Modern browsers can use jQuery.cssProps as a basic hook
	$.cssProps[propertyName] = supportProperty;
	
	// Firefox needs a complete hook because it stuffs matrix with 'px'
	if ( supportProperty == 'Moz' + suffix ) {
		propertyHook = {
			get: function( elem, computed ) {
				return (computed ?
					// remove 'px' from the computed matrix
					$.css( elem, supportProperty ).split('px').join(''):
					elem.style[supportProperty]
				)
			},
			set: function( elem, value ) {
				// remove 'px' from matrices
				elem.style[supportProperty] = /matrix[^)p]*\)/.test(value) ?
					value.replace(/matrix((?:[^,]*,){4})([^,]*),([^)]*)/, 'matrix$1$2px,$3px'):
					value;
			}
		}
	/* Fix two jQuery bugs still present in 1.5.1
	 * - rupper is incompatible with IE9, see http://jqbug.com/8346
	 * - jQuery.css is not really jQuery.cssProps aware, see http://jqbug.com/8402
	 */
	} else if ( /^1\.[0-5](?:\.|$)/.test($.fn.jquery) ) {
		propertyHook = {
			get: function( elem, computed ) {
				return (computed ?
					$.css( elem, supportProperty.replace(/^ms/, 'Ms') ):
					elem.style[supportProperty]
				)
			}
		}
	}
	/* TODO: leverage hardware acceleration of 3d transform in Webkit only
	else if ( supportProperty == 'Webkit' + suffix && support3dTransform ) {
		propertyHook = {
			set: function( elem, value ) {
				elem.style[supportProperty] = 
					value.replace();
			}
		}
	}*/
	
} else if ( supportMatrixFilter ) {
	propertyHook = {
		get: function( elem, computed ) {
			var elemStyle = ( computed && elem.currentStyle ? elem.currentStyle : elem.style ),
				matrix;

			if ( elemStyle && rMatrix.test( elemStyle.filter ) ) {
				matrix = RegExp.$1.split(',');
				matrix = [
					matrix[0].split('=')[1],
					matrix[2].split('=')[1],
					matrix[1].split('=')[1],
					matrix[3].split('=')[1]
				];
			} else {
				matrix = [1,0,0,1];
			}
			matrix[4] = elemStyle ? elemStyle.left : 0;
			matrix[5] = elemStyle ? elemStyle.top : 0;
			return "matrix(" + matrix + ")";
		},
		set: function( elem, value, animate ) {
			var elemStyle = elem.style,
				currentStyle,
				Matrix,
				filter;

			if ( !animate ) {
				elemStyle.zoom = 1;
			}

			value = matrix(value);

			// rotate, scale and skew
			if ( !animate || animate.M ) {
				Matrix = [
					"Matrix("+
						"M11="+value[0],
						"M12="+value[2],
						"M21="+value[1],
						"M22="+value[3],
						"SizingMethod='auto expand'"
				].join();
				filter = ( currentStyle = elem.currentStyle ) && currentStyle.filter || elemStyle.filter || "";

				elemStyle.filter = rMatrix.test(filter) ?
					filter.replace(rMatrix, Matrix) :
					filter + " progid:DXImageTransform.Microsoft." + Matrix + ")";

				// center the transform origin, from pbakaus's Transformie http://github.com/pbakaus/transformie
				if ( (centerOrigin = $.transform.centerOrigin) ) {
					elemStyle[centerOrigin == 'margin' ? 'marginLeft' : 'left'] = -(elem.offsetWidth/2) + (elem.clientWidth/2) + 'px';
					elemStyle[centerOrigin == 'margin' ? 'marginTop' : 'top'] = -(elem.offsetHeight/2) + (elem.clientHeight/2) + 'px';
				}
			}

			// translate
			if ( !animate || animate.T ) {
				// We assume that the elements are absolute positionned inside a relative positionned wrapper
				elemStyle.left = value[4] + 'px';
				elemStyle.top = value[5] + 'px';
			}
		}
	}
}
// populate jQuery.cssHooks with the appropriate hook if necessary
if ( propertyHook ) {
	$.cssHooks[propertyName] = propertyHook;
}
// we need a unique setter for the animation logic
propertyGet = propertyHook && propertyHook.get || $.css;

/*
 * fn.animate() hooks
 */
$.fx.step.transform = function( fx ) {
	var elem = fx.elem,
		start = fx.start,
		end = fx.end,
		split,
		pos = fx.pos,
		transform,
		translate,
		rotate,
		scale,
		skew,
		T = false,
		M = false,
		prop;
	translate = rotate = scale = skew = '';

	// fx.end and fx.start need to be converted to their translate/rotate/scale/skew components
	// so that we can interpolate them
	if ( !start || typeof start === "string" ) {
		// the following block can be commented out with jQuery 1.5.1+, see #7912
		if (!start) {
			start = propertyGet( elem, supportProperty );
		}

		// force layout only once per animation
		if ( supportMatrixFilter ) {
			elem.style.zoom = 1;
		}

		// if the start computed matrix is in end, we are doing a relative animation
		split = end.split(start);
		if ( split.length == 2 ) {
			// remove the start computed matrix to make animations more accurate
			end = split.join('');
			fx.origin = start;
			start = 'none';
		}

		// start is either 'none' or a matrix(...) that has to be parsed
		fx.start = start = start == 'none'?
			{
				translate: [0,0],
				rotate: 0,
				scale: [1,1],
				skew: [0,0]
			}:
			unmatrix( toArray(start) );

		// fx.end has to be parsed and decomposed
		fx.end = end = ~end.indexOf('matrix')?
			// bullet-proof parser
			unmatrix(matrix(end)):
			// faster and more precise parser
			components(end);

		// get rid of properties that do not change
		for ( prop in start) {
			if ( prop == 'rotate' ?
				start[prop] == end[prop]:
				start[prop][0] == end[prop][0] && start[prop][1] == end[prop][1]
			) {
				delete start[prop];
			}
		}
	}

	/*
	 * We want a fast interpolation algorithm.
	 * This implies avoiding function calls and sacrifying DRY principle:
	 * - avoid $.each(function(){})
	 * - round values using bitewise hacks, see http://jsperf.com/math-round-vs-hack/3
	 */
	if ( start.translate ) {
		// round translate to the closest pixel
		translate = ' translate('+
			((start.translate[0] + (end.translate[0] - start.translate[0]) * pos + .5) | 0) +'px,'+
			((start.translate[1] + (end.translate[1] - start.translate[1]) * pos + .5) | 0) +'px'+
		')';
		T = true;
	}
	if ( start.rotate != undefined ) {
		rotate = ' rotate('+ (start.rotate + (end.rotate - start.rotate) * pos) +'rad)';
		M = true;
	}
	if ( start.scale ) {
		scale = ' scale('+
			(start.scale[0] + (end.scale[0] - start.scale[0]) * pos) +','+
			(start.scale[1] + (end.scale[1] - start.scale[1]) * pos) +
		')';
		M = true;
	}
	if ( start.skew ) {
		skew = ' skew('+
			(start.skew[0] + (end.skew[0] - start.skew[0]) * pos) +'rad,'+
			(start.skew[1] + (end.skew[1] - start.skew[1]) * pos) +'rad'+
		')';
		M = true;
	}

	// In case of relative animation, restore the origin computed matrix here.
	transform = fx.origin ?
		fx.origin + translate + skew + scale + rotate:
		translate + rotate + scale + skew;

	propertyHook && propertyHook.set ?
		propertyHook.set( elem, transform, {M: M, T: T} ):
		elem.style[supportProperty] = transform;
};

/*
 * Utility functions
 */

// turns a transform string into its 'matrix(A,B,C,D,X,Y)' form (as an array, though)
function matrix( transform ) {
	transform = transform.split(')');
	var
			trim = $.trim
		// last element of the array is an empty string, get rid of it
		, i = transform.length -1
		, split, prop, val
		, A = 1
		, B = 0
		, C = 0
		, D = 1
		, A_, B_, C_, D_
		, tmp1, tmp2
		, X = 0
		, Y = 0
		;
	// Loop through the transform properties, parse and multiply them
	while (i--) {
		split = transform[i].split('(');
		prop = trim(split[0]);
		val = split[1];
		A_ = B_ = C_ = D_ = 0;

		switch (prop) {
			case 'translateX':
				X += parseInt(val, 10);
				continue;

			case 'translateY':
				Y += parseInt(val, 10);
				continue;

			case 'translate':
				val = val.split(',');
				X += parseInt(val[0], 10);
				Y += parseInt(val[1] || 0, 10);
				continue;

			case 'rotate':
				val = toRadian(val);
				A_ = Math.cos(val);
				B_ = Math.sin(val);
				C_ = -Math.sin(val);
				D_ = Math.cos(val);
				break;

			case 'scaleX':
				A_ = val;
				D_ = 1;
				break;

			case 'scaleY':
				A_ = 1;
				D_ = val;
				break;

			case 'scale':
				val = val.split(',');
				A_ = val[0];
				D_ = val.length>1 ? val[1] : val[0];
				break;

			case 'skewX':
				A_ = D_ = 1;
				C_ = Math.tan(toRadian(val));
				break;

			case 'skewY':
				A_ = D_ = 1;
				B_ = Math.tan(toRadian(val));
				break;

			case 'skew':
				A_ = D_ = 1;
				val = val.split(',');
				C_ = Math.tan(toRadian(val[0]));
				B_ = Math.tan(toRadian(val[1] || 0));
				break;

			case 'matrix':
				val = val.split(',');
				A_ = +val[0];
				B_ = +val[1];
				C_ = +val[2];
				D_ = +val[3];
				X += parseInt(val[4], 10);
				Y += parseInt(val[5], 10);
		}
		// Matrix product
		tmp1 = A * A_ + B * C_;
		B    = A * B_ + B * D_;
		tmp2 = C * A_ + D * C_;
		D    = C * B_ + D * D_;
		A = tmp1;
		C = tmp2;
	}
	return [A,B,C,D,X,Y];
}

// turns a matrix into its rotate, scale and skew components
// algorithm from http://hg.mozilla.org/mozilla-central/file/7cb3e9795d04/layout/style/nsStyleAnimation.cpp
function unmatrix(matrix) {
	var
			scaleX
		, scaleY
		, skew
		, A = matrix[0]
		, B = matrix[1]
		, C = matrix[2]
		, D = matrix[3]
		;

	// Make sure matrix is not singular
	if ( A * D - B * C ) {
		// step (3)
		scaleX = Math.sqrt( A * A + B * B );
		A /= scaleX;
		B /= scaleX;
		// step (4)
		skew = A * C + B * D;
		C -= A * skew;
		D -= B * skew;
		// step (5)
		scaleY = Math.sqrt( C * C + D * D );
		C /= scaleY;
		D /= scaleY;
		skew /= scaleY;
		// step (6)
		if ( A * D < B * C ) {
			//scaleY = -scaleY;
			//skew = -skew;
			A = -A;
			B = -B;
			skew = -skew;
			scaleX = -scaleX;
		}

	// matrix is singular and cannot be interpolated
	} else {
		rotate = scaleX = scaleY = skew = 0;
	}

	return {
		translate: [+matrix[4], +matrix[5]],
		rotate: Math.atan2(B, A),
		scale: [scaleX, scaleY],
		skew: [skew, 0]
	}
}

// parse tranform components of a transform string not containing 'matrix(...)'
function components( transform ) {
	// split the != transforms
  transform = transform.split(')');

	var translate = [0,0],
    rotate = 0,
    scale = [1,1],
    skew = [0,0],
    i = transform.length -1,
    trim = $.trim,
    split, name, value;

  // add components
  while ( i-- ) {
    split = transform[i].split('(');
    name = trim(split[0]);
    value = split[1];
    
    if (name == 'translateX') {
      translate[0] += parseInt(value, 10);

    } else if (name == 'translateY') {
      translate[1] += parseInt(value, 10);

    } else if (name == 'translate') {
      value = value.split(',');
      translate[0] += parseInt(value[0], 10);
      translate[1] += parseInt(value[1] || 0, 10);

    } else if (name == 'rotate') {
      rotate += toRadian(value);

    } else if (name == 'scaleX') {
      scale[0] *= value;

    } else if (name == 'scaleY') {
      scale[1] *= value;

    } else if (name == 'scale') {
      value = value.split(',');
      scale[0] *= value[0];
      scale[1] *= (value.length>1? value[1] : value[0]);

    } else if (name == 'skewX') {
      skew[0] += toRadian(value);

    } else if (name == 'skewY') {
      skew[1] += toRadian(value);

    } else if (name == 'skew') {
      value = value.split(',');
      skew[0] += toRadian(value[0]);
      skew[1] += toRadian(value[1] || '0');
    }
	}

  return {
    translate: translate,
    rotate: rotate,
    scale: scale,
    skew: skew
  };
}

// converts an angle string in any unit to a radian Float
function toRadian(value) {
	return ~value.indexOf('deg') ?
		parseInt(value,10) * (Math.PI * 2 / 360):
		~value.indexOf('grad') ?
			parseInt(value,10) * (Math.PI/200):
			parseFloat(value);
}

// Converts 'matrix(A,B,C,D,X,Y)' to [A,B,C,D,X,Y]
function toArray(matrix) {
	// Fremove the unit of X and Y for Firefox
	matrix = /\(([^,]*),([^,]*),([^,]*),([^,]*),([^,p]*)(?:px)?,([^)p]*)(?:px)?/.exec(matrix);
	return [matrix[1], matrix[2], matrix[3], matrix[4], matrix[5], matrix[6]];
}

$.transform = {
	centerOrigin: 'margin'
};

})( jQuery );
