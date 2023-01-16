<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>overview</id>
		<name>$yaha_tuid:heating$</name>
		<order>0</order>
		<icon>yaha_heating</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			LOG_PATH             = "yaha/logs/"
			LOG_FILE_NAME_SUFFIX = ".csv"
			TREND_FILE_NAME_TRUNK  = "heating"
			STATISTICS_FILE_NAME_TRUNK  = "statistics_"
				
			var COLOR_YAHA_BLUE = "#0C4FFF"
			var ChartLegendTranslation = {}
			
				
			function onClickLanguageSelector(jqElement)
			{
				yvSwitchLanguage(jqElement.attr('href').substr(1))
			}
	
			function moduleInit()
			{
				//clear current languages 
				$("#languageSelector a").remove()
			
				//create new buttons according to list
				var mainNavHtmlString = ""
				for (languageID in AvailableLanguages)
				{
					mainNavHtmlString += '<a href="#' + languageID + '" class="ui-btn ui-corner-all ui-icon-yaha_flag_' + languageID + ' ui-nodisc-icon ui-btn-icon-left" style="text-align: left" onclick="onClickLanguageSelector($(this))">' + AvailableLanguages[languageID] + '</a>'
				}
				
				$(mainNavHtmlString).appendTo('#languageSelector');

				/* get current date and time of local machine when ever the user opens this module */
				getTimeFromLocalMachine();

				/* Show main navigation when overview page */
				//$( "#panelMainNav" ).panel( "open" );
				
				//initial drawing of heat curves
				heatCurveFloorHeatingHandle = initHeatcurve("canvasHeatcurveFloorHeating", COLOR_YAHA_BLUE)
				refreshHeatCurve(heatCurveFloorHeatingHandle, "floorHeatingSetTemp","floorHeatCurveSlope", "floorHeatCurveLevel")

				//initial drawing of heat curves
				heatCurveRadiatorHeatingHandle = initHeatcurve("canvasHeatcurveRadiatorHeating", COLOR_YAHA_BLUE)
				refreshHeatCurve(heatCurveRadiatorHeatingHandle, "radiatorHeatingSetTemp","radiatorHeatCurveSlope", "radiatorHeatCurveLevel")


				//get legend translations and then draw the charts
				var cgiData = {}
				cgiData["requestType"] = "getLegendTranslation";
				cgiData["language"] = ActiveLanguage;
			
				jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
					function(jsonDataFromServer,status)
				    {	
						//data from server comes in JSON format => convert to JavaScript object
						ChartLegendTranslation =jQuery.parseJSON(jsonDataFromServer)

						//Statistics chart
						statisticsLineChartInit()
		
						//Trend oscilloscope 
						trendLineChartInit()

						drawTrend()
				    });	
				    
				//set up PDI monitor just a bit once everything is loaded to avoid funny interference with jQuery!?
				setTimeout(pdiMonitorInit, 100)
				
				//knob widget init
				knobWidgetInit(	"floorHeatingReducedTempKnob",		//id of knob container
								"floorHeatingReducedTempBars", 		//id of bar container
								0, 									//snap to 0 value
								25,									//start value of knob
								15, 								//minimum value
								25, 								//maximum value
								0.5, 								//step witdh of value
								0, 									//rotation limit: minimum degree
								181, 								//rotation limit: maximum degree
								12, 								//spacing degree between two bars
								"floorHeatingReducedTemp")			//id of tag in which current value will be written and monitored to adjust knob rotation on change


				//show or hide on load
				if ($('input[name=heatingmode]:checked', '#form_operating_mode').val() == 3) //not at home mode
				{
					$("#notAtHome_details_leaving").show()
					$("#notAtHome_details_backhome").show()			
				}
				else
				{
					$("#notAtHome_details_leaving").hide()
					$("#notAtHome_details_backhome").hide()			
				}
	

			}
			

			function getTimeFromLocalMachine()
			{
				/* get current date of local machine which runs the browser to initalize input fields for usability */
				setDate = new Date()	
				$("#setDateString").val(setDate.toISOString().substring(0, 10));
				setHours = ""
				setHours += setDate.getHours()
				if (setHours.length == 1)
				{
					setHours = "0" + setHours;		//add leading zero otherwise input field will not accept it: 09:00
				}
				
				setMinutes = ""
				setMinutes += setDate.getMinutes()
				if (setMinutes.length == 1)
				{
					setMinutes = "0" + setMinutes;		//add leading zero otherwise input field will not accept it: 09:00
				}

				/* apply time to input field */
				$("#setTimeString").val( setHours + ":" + setMinutes)
			}
			
			/* dynamic display of not at home parameters /Begin */
			//show or hide on if selected or deselected
			$('#form_operating_mode input').on('change', function() 
														{
															if ($('input[name=heatingmode]:checked', '#form_operating_mode').val() == 3) //not at home mode
															{
																$("#notAtHome_details_leaving").show()
																$("#notAtHome_details_backhome").show()			
															}
															else
															{
																$("#notAtHome_details_leaving").hide()
																$("#notAtHome_details_backhome").hide()			
															}
														});
			/* dynamic display of not at home parameters /End */

			function initHeatcurve(canvasID, lineColor)
			{
				/* https://dima117.github.io/Chart.Scatter/ */
				var heatCurveCanvas = document.getElementById(canvasID).getContext("2d");
	
				var data = [
				    {
				      strokeColor: lineColor,
				      pointColor: lineColor,
				      pointStrokeColor: '#fff',
				      data: []			//data will be dynamically added by formula calculation
				    }
				  ];
				  
				var options = [
					{
						showScale: true,
						pointDot: false
					}
				];			
							
				var chartHandle = new Chart(heatCurveCanvas).Scatter(data, options);
					
				return chartHandle
			}


			function refreshHeatCurve(chartHandle, t_room_set_ID, t_slope_ID, level_ID)
			{
				curNbDataPoints = chartHandle.datasets[0].points.length
				for (i = 0; i < curNbDataPoints; i++) 
				{
					//always delete first point as array would dynamically change its size due to removing points
					chartHandle.datasets[0].removePoint(0)
				}

				var outTempMin = -30.0		//hard coded range for temperature
				var outTempMax = 20.0
				var outTempStep = 5.0		//step with for formula calculation

				var roomSetTemp = parseFloat(document.getElementById(t_room_set_ID).value);
				var slope = parseFloat(document.getElementById(t_slope_ID).value);
				var level = parseFloat(document.getElementById(level_ID).value);
				var flowTemp = 0
				
				for (outTemp = outTempMin; outTemp <= outTempMax; outTemp += outTempStep)
				{
					//t_flow = t_room_set+slope*20*((t_room_set-t_out)/20)^0,8+level
					flowTemp = roomSetTemp + slope * 20 * Math.pow((roomSetTemp - outTemp)/20,0.8) + level
					
					//put point on chart
					chartHandle.datasets[0].addPoint(outTemp, flowTemp.toFixed(2)); //two decimal places to have a more readable value when hover over chart points 
				}
				
				chartHandle.update()
			}
			
			//wrapper function for onchange events
			function onChangeHeatCurveFloorHeating()
			{
				refreshHeatCurve(heatCurveFloorHeatingHandle, "floorHeatingSetTemp","floorHeatCurveSlope", "floorHeatCurveLevel")			
			}

			function onChangeHeatCurveRadiatorHeating()
			{
				refreshHeatCurve(heatCurveRadiatorHeatingHandle, "radiatorHeatingSetTemp","radiatorHeatCurveSlope", "radiatorHeatCurveLevel")
			}

			//bind curve update function to all all fields which influences the curve
			$( "#floorHeatCurveLevel" ).change(function() 
									{
						  				onChangeHeatCurveFloorHeating();
									});
			$( "#floorHeatCurveSlope" ).change(function() 
									{
						  				onChangeHeatCurveFloorHeating();
									});
			$( "#floorHeatingSetTemp" ).change(function() 
									{
						  				onChangeHeatCurveFloorHeating();
									});
			
			$( "#radiatorHeatCurveLevel" ).change(function() 
									{
						  				onChangeHeatCurveRadiatorHeating();
									});
			$( "#radiatorHeatCurveSlope" ).change(function() 
									{
						  				onChangeHeatCurveRadiatorHeating();
									});
			$( "#radiatorHeatingSetTemp" ).change(function() 
									{
						  				onChangeHeatCurveRadiatorHeating();
									});
			

			function tagEnableDisable(switchId, tagId)
			{
				if (document.getElementById(switchId).checked == false)
				{
					$('#' + tagId + ' *').attr('disabled', 'disabled');
				}
				else
				{
					$('#' + tagId + ' *').removeAttr('disabled');
				}

			}


			function trendLineChartInit()
			{
				//start recording
				$(document).on("click", "#cmdRecorderStart",
					function(event)
					{
						setTimeout(function(){ drawTrend() }, 1000)
					});		

				//stop recording and refresh chart
				$(document).on("click", "#cmdRecorderStop",
					function(event)
					{
						setTimeout(function(){ drawTrend() }, 1000)
					});		
				
				//force refresh of line chart in case the file has been deleted					
				$(document).on("click", "#cmdRecorderClear",
					function(event)
					{
						setTimeout(function(){ drawTrend() }, 1000)
					});		

				//manuelly refresh chart
				$(document).on("click", "#trendChartRefresh",
					function(event)
					{
						drawTrend()
					});		
			}

			function drawTrend()
			{
				fileName = LOG_PATH + TREND_FILE_NAME_TRUNK + LOG_FILE_NAME_SUFFIX

				drawLineChart("trend_chart", fileName, "$all$", "%Y.%m.%d %H:%M:%S", "%H:%M:%S", "", 15, ChartLegendTranslation)		
			}


			function statisticsLineChartInit()
			{
				var currentDate = new Date();
				var currentYear = currentDate.getFullYear();
				
				//set input field to current year
				$("#yearLog").val(currentYear)

				fileName = LOG_PATH + STATISTICS_FILE_NAME_TRUNK + currentYear + LOG_FILE_NAME_SUFFIX
				console.log(fileName)

				drawLineChart("statistics_linechart", fileName, "$all$", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15, ChartLegendTranslation, 5)
			
				//add event in case year has been updated
				$(document).on("keypress", "#yearLog",
					function(event)
					{
						//console.log(event)

						var keycode = (event.keyCode ? event.keyCode : event.which);	//compatibility: use event.which if keyCode does not exists
						if (keycode == '13')	//enter key
						{
							fileName = LOG_PATH + STATISTICS_FILE_NAME_TRUNK + $("#yearLog").val() + LOG_FILE_NAME_SUFFIX
							drawLineChart("statistics_linechart", fileName, "$all$", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15, ChartLegendTranslation, 5)
						}
						else
						{
							//in case of any other key ignore it		
							return
						}
	
					});			

				$(document).on("blur", "#yearLog",
					function(event)
					{
						fileName = LOG_PATH + STATISTICS_FILE_NAME_TRUNK + $("#yearLog").val() + LOG_FILE_NAME_SUFFIX
						drawLineChart("statistics_linechart", fileName, "$all$", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15, ChartLegendTranslation, 5)
					});	

			
			}


			//++++++++++++++++++++++++++++++++++++++ PDI MONITOR SCRIPTING /Begin ++++++++++++++++++++++++++++++++++++++
			var PdiMonitorRowIndex;	
			var PdiMonitorTagsInTable = {}

			function pdiMonitorInit()
			{
				PdiMonitorRowIndex = 2;		//index of second row in table which is the first data row after the header row
				PdiMonitorTagsInTable = {}	//tag:input-ID

				//rebuild last table configuration
				cookieTagList = monitorReadTagListFromCookie()
				for (tag in cookieTagList)
				{	
					//add all valid tags into table
					if (cookieTagList[tag] != "")
					{
						addPdiMonitorRowToTable()
						lastRowIndex = PdiMonitorRowIndex - 1
						$("#" + "tag_name" + lastRowIndex).val(cookieTagList[tag])
					}
				}

				//hook call back function in juice frame work to get monitor data once processed by the juice frame work
				yjAddPostUpdateUiFunctionMonitorLiveData(monitorUiUpdate)

				//when table has been build up rebuild monitor table
				rebuildPdiMonitorTagsInTable()
			}

			//add new tag in table
			$("#pdi_mon_add_tag").on('click',function(){
				addPdiMonitorRowToTable()
			});

			//delete tag from table
			$("#pdi_mon_delete_tag").on('click', function() {
				$('.pdi_mon_tag_row:checkbox:checked').parents("tr").remove();
			    $('.pdi_mon_check_all').prop("checked", false); 
				check();
	
				//when table has been modified rebuild monitor table
				rebuildPdiMonitorTagsInTable()
			});
			
			//add one row to the table
			function addPdiMonitorRowToTable()
			{
				//prepare html code for table row
				var cell_html_string_checkbox  = "<td><input type='checkbox' class='pdi_mon_tag_row'/></td>"
				var cell_html_string_tag_name  = "<td><input type='text' id='tag_name"  + PdiMonitorRowIndex + "' name='tag_name[]'/></td>"
				var cell_html_string_tag_value = "<td><input type='text' id='tag_value" + PdiMonitorRowIndex + "' name='tag_value[]'/></td>"

			    var row_html_string= "";
			    row_html_string += "<tr>";
			    row_html_string += cell_html_string_checkbox
			    row_html_string += cell_html_string_tag_name
			    row_html_string += cell_html_string_tag_value
			    row_html_string +="</tr>";
				
				//add row to table
				$('#pdi_monitor').append(row_html_string);
				
				//add event listener for tag name which should be monitored
				$("#tag_name" + PdiMonitorRowIndex).on('change', function() {
					//PdiMonitorTagsInTable[$(this).val()] = this.id			//tag name = id of input field
					//console.log(PdiMonitorTagsInTable)

					//when table has been modified rebuild monitor table
					rebuildPdiMonitorTagsInTable()
				});				
				
				//add event listener for tag value which should be writte on change
				$("#tag_value" + PdiMonitorRowIndex).on('change', function() {
					tagValue = $(this).val() //current value of PDI tag to write

					//find input field in second column of row with PDI tag name corresponding to the value in third columns 
					//this = input-ID showing tag value -> parent() is its cell: <td> element -> parent() is its row: <tr> element 
					rowObj = $(this).parent().parent()
					//once we have the row -> access input field cell of second column and read current PDI tag name 
					tagName = rowObj.children("td:nth-child(2)").children('input').val() 

					yjAddMonitorTagToWriteCgiData(tagName, tagValue)					//hand over name and value of tag to juice frame work to write to server
				});				
				
				PdiMonitorRowIndex++;
			}
			

			//rebuild tag dictionary from current table entries
			function rebuildPdiMonitorTagsInTable()
			{
				PdiMonitorTagsInTable = {} 

				//go through second column of table and access input field
				$("#pdi_monitor").children("tbody").children("tr").children("td:nth-child(2)").children('input').each(function () {
					PdiMonitorTagsInTable[$(this).val()] = this.id			//tag name = id of input field
					//console.log(PdiMonitorTagsInTable)
				});

				//rebuild also cyclic read list for juice framework
				updateCyclicReadList()
				
				//keep current configuration as cookie in mind
				monitorWriteCookie(PdiMonitorTagsInTable)
			}

			
			//go through all currently tags entered in table and create a read list 
			function updateCyclicReadList()
			{
				var readCyclicMonitorTagIDs = new Array()

				//key of dictionary is tag name
				for (tag in PdiMonitorTagsInTable)
				{
					readCyclicMonitorTagIDs.push(tag)
				}
				
				//send list to juice framework
				yjDefineMonitorCyclicReadTagList(readCyclicMonitorTagIDs)
			}

			//update monitor table with live values
			function monitorUiUpdate(monitorLiveData)
			{
				for (tag in monitorLiveData)
				{
					//find third column of row to display value of tag
					//PdiMonitorTagsInTable[tag] = input-ID of this tag -> parent() is its cell: <td> element -> parent() is its row: <tr> element 
					rowObj = $('#' + PdiMonitorTagsInTable[tag]).parent().parent()
					
					//once we have the row -> access input field cell of third column and write current live value
					rowObj.children("td:nth-child(3)").children('input').each(function () 
																				{
																					//skip refresh of user interface if element has focus (user is editing)
																					if (this.id != document.activeElement.id)
																					{
																						$(this).val(monitorLiveData[tag])
																					}
																				});		
					
				}
			}


			function monitorWriteCookie(tagsInTable)
			{
				var tagListString = ""

				//key of dictionary is tag name
				for (tag in tagsInTable)
				{
					tagListString = tagListString.concat(tag)
					tagListString = tagListString.concat(",")
				}
								
				Cookies.set('COOKIE_YAHA_PDI_MONITOR', tagListString, { expires: 365 });  
			}
			
			
			function monitorReadTagListFromCookie()
			{
				tagList = []
				
				/* read cookies */
				tagListString = Cookies.get('COOKIE_YAHA_PDI_MONITOR')

				try 
				{
					if (tagListString.length > 0)
					{
						tagList = tagListString.split(",");
					}	
				}
				catch(err) 
				{
					tagList = []
				}					
				
				return tagList
			}


			
			function pdi_mon_select_all_tags() {
				$('input[class=pdi_mon_tag_row]:checkbox').each(function(){ 
					if($('input[class=pdi_mon_check_all]:checkbox:checked').length == 0){ 
						$(this).prop("checked", false); 
					} else {
						$(this).prop("checked", true); 
					} 
				});
			}
			
			function check(){
				obj=$('#pdi_monitor tr').find('input');
				$.each( obj, function( key, value ) {
				id=value.id;
				$('#'+id).html(key+1);
				});
				}


			//++++++++++++++++++++++++++++++++++++++ PDI MONITOR SCRIPTING /End ++++++++++++++++++++++++++++++++++++++

			
		</script>

	  	<!-- the following line stores the flags used to send button trigger to server -->
		<div style="visibility:hidden">
			<span id="floorHeatingState" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolFloorHeatingState ; symbol_map:0=yaha-symbol-night,1=yaha-symbol-weather-sun,2=yaha-symbol-heating-off"></span>
			<span id="radiatorHeatingState" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolRadiatorHeatingState ; symbol_map:0=yaha-symbol-night,1=yaha-symbol-weather-sun,2=yaha-symbol-heating-off"></span>

			<span id="burnerAlarmOverTemp" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:burnerAlarmOverTempEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="burnerAlarmFault" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:burnerAlarmFaultEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="alarmModbusNoConnection" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:alarmModbusNoConnectionEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="alarmIOsimulationActive" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:alarmIOsimulationEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="globalHeatingMode" style="visibility:hidden" yaha="io_mode:read_cyclic; radio_map:0=globalHeatingModeOff,1=globalHeatingModeOn,2=globalHeatingModeSuspend,3=globalHeatingModeNotAtHome"></span>
			<span id="floorHeatingMode" style="visibility:hidden" yaha="io_mode:read_cyclic; radio_map:0=floorHeatingModeAuto,1=floorHeatingModeComfort,2=floorHeatingModeReduced"></span>
			<span id="radiatorHeatingMode" style="visibility:hidden" yaha="io_mode:read_cyclic; radio_map:0=radiatorHeatingModeAuto,1=radiatorHeatingModeComfort,2=radiatorHeatingModeReduced"></span>
			<span id="hotwaterState" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolHotwaterState ; symbol_map:0=yaha-symbol-fire-bw,1=yaha-symbol-fire"></span>
			<span id="floorPumpAlarmFrostProtect" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:floorPumpAlarmFrostProtectEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="radiatorPumpAlarmFrostProtect" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:radiatorPumpAlarmFrostProtectEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="floorPumpAlarmSafetyReleaseOff" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:floorPumpAlarmSafetyReleaseOffEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="radiatorPumpAlarmSafetyReleaseOff" style="visibility:hidden" yaha="io_mode:read_cyclic ; effect_target_id:radiatorPumpAlarmSafetyReleaseOffEffect ; effect_type:visibility ; effect_value_map:0=hide,1=show"></span>
			<span id="floorHeatingControllerState" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolFloorHeatingControllerState ; symbol_map:0=yaha-symbol-controller-off,1=yaha-symbol-controller-on"></span>
			<span id="radiatorHeatingControllerState" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolRadiatorHeatingControllerState ; symbol_map:0=yaha-symbol-controller-off,1=yaha-symbol-controller-on"></span>

			<span id="burnerState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_boiler_on_off ; anim_attribute:style,fill ; anim_attr_val_map:0=#cccccc,1=#ff5800"></span>
			<span id="floorPumpState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_floor_pump ; anim_attribute:style,fill ; anim_attr_val_map:0=#ffffff,1=#ff0000"></span>
			<span id="radiatorPumpState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_radiator_pump ; anim_attribute:style,fill ; anim_attr_val_map:0=#ffffff,1=#ff0000"></span>
			<span id="hotwaterPumpState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_hotwater_pump ; anim_attribute:style,fill ; anim_attr_val_map:0=#ffffff,1=#ff0000"></span>
			<span id="actTempFlowRadiator" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_radiator_temp_flow_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="actTempFlowFloor" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_floor_temp_flow_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="actTempHotwater" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_boiler_temp_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="actTempBurner" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_burner_temp_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="burnerSetTemp" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_burner_temp_set ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="actTempOutsideNorth" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_outside_north_temp_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="floorHeatingMixerActPosition" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_floor_mixer_pos_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:%>% show"></span>
			<span id="radiatorHeatingMixerActPosition" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_radiator_mixer_pos_act ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:%>% show"></span>
			<span id="floorHeatingMixerState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_floor_mixer_state ; anim_attribute:style,fill ; anim_attr_val_map:0=#ffffff,1=#0000ff,2=#ff0000,3=#cccccc"></span>
			<span id="radiatorHeatingMixerState" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_radiator_mixer_state ; anim_attribute:style,fill ; anim_attr_val_map:0=#ffffff,1=#0000ff,2=#ff0000,3=#cccccc"></span>
			<span id="floorHeatingSetFlowTemp" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_floor_flow_temp_set ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="radiatorHeatingSetFlowTemp" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_radiator_flow_temp_set ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>
			<span id="hotwaterResultSetTemp" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:heatingCircuitSVG ; anim_svg_item_id:hc_boiler_temp_set ; anim_attribute:textContent ; anim_format:0.0 ; anim_unit:$deg$C>$deg$C show"></span>

		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="recorderCmdStart" yaha="tag_group:RECORDER_CMD_START">1</span>
			<span id="recorderCmdStop" yaha="tag_group:RECORDER_CMD_STOP">1</span>
			<span id="recorderCmdClear" yaha="tag_group:RECORDER_CMD_CLEAR">1</span>
		</div>	


		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:dashboard$ ; module_icon: yaha_dashboard; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:dashboard$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:floorheating$</h3>

						<table>	
							<tbody>						
					  			<tr>
									<td>
										<span>$yaha_tuid:acttemperature$ $yaha_tuid:lounge$</span>
									</td>
									<td>
										<span id="actTempRoomLounge" yaha="io_mode:read_cyclic ; format:0.0">0.0</span><span> &#8451;</span>
									</td>
									<td>
										<span id="symbolFloorHeatingState" class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
										<span id="symbolFloorHeatingControllerState" class="yaha-symbol yaha-symbol-controller-off" style="width: 40px; line-height: 30px;"></span>
									</td>
					  			</tr>		
					  		</tbody>
					  	</table>

						<table>	
							<tbody>						
							  	<tr style="height:1em;"></tr>

					  			<tr>
									<td colspan=3 style="width:300px">$yaha_tuid:desiredcomforttemperature$</td>
					  			</tr>		
					  			
					  			<tr>
					  				<td style="width:30%">
										<span style="font-size:200%;" id="floorHeatingSetTempSliderText"></span> <span style="font-size:200%;">&deg;C</span>							
									</td>
									<td colspan=2>
										<input 
										id="floorHeatingSetTemp"
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: floorHeatingSetTempSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:radiatorheating$</h3>

						<table>	
							<tbody>						
					  			<tr>
									<td>
										<span>$yaha_tuid:acttemperature$ $yaha_tuid:library$</span>
									</td>
									<td>
										<span id="actTempRoomLibrary" yaha="io_mode:read_cyclic ; format:0.0">0.0</span><span> &#8451;</span>
									</td>
									<td>
										<span id="symbolRadiatorHeatingState" class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
										<span id="symbolRadiatorHeatingControllerState" class="yaha-symbol yaha-symbol-controller-off" style="width: 40px; line-height: 30px;"></span>
									</td>
					  			</tr>		
					  		</tbody>
					  	</table>
					  	
						<table>	
							<tbody>						
							  	<tr style="height:1em;"></tr>

					  			<tr>
									<td colspan=3 style="width:300px">$yaha_tuid:desiredcomforttemperature$</td>
					  			</tr>		
					  			
					  			<tr>
					  				<td style="width:30%">
										<span style="font-size:200%;" id="radiatorHeatingSetTempSliderText"></span> <span style="font-size:200%;">&deg;C</span>							
									</td>
									<td colspan=2>
										<input 
										id="radiatorHeatingSetTemp"
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: radiatorHeatingSetTempSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:alarmmessages$</h3>

						<table>	
							<tbody>						
					  			<tr>
					  				<td><span id="burnerAlarmOverTempEffect" class="blink" style="color:red; display:none">$yaha_tuid:burnerovertemperatur$</span></td>
					  			</tr>						
					  			<tr>
					  				<td><span id="burnerAlarmFaultEffect" class="blink" style="color:red; display:none">$yaha_tuid:burnerfault$</span></td>
					  			</tr>
					  			<tr>
					  				<td><span id="alarmModbusNoConnectionEffect" class="blink" style="color:red; display:none">$yaha_tuid:modbusheatingio$</span></td>
					  			</tr>
					  			<tr>
					  				<td><span id="alarmIOsimulationEffect" style="color:red; display:none">$yaha_tuid:iosimulationactive$</span></td>
					  			</tr>
					  		</tbody>
					  	</table>				
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:heatingmode$</h3>

						<form id="form_operating_mode">
					        <fieldset data-role="controlgroup">
								<table>	
									<tbody>						
							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-switched-on" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="globalHeatingModeOn" value="1" yaha="io_mode:write_change ; radio_target_pdi_tag:globalHeatingMode">
									        <label for="globalHeatingModeOn">$yaha_tuid:switchedon$</label></td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-heating-off" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="globalHeatingModeOff" value="0" yaha="io_mode:write_change ; radio_target_pdi_tag:globalHeatingMode">
									        <label for="globalHeatingModeOff">$yaha_tuid:switchedoff$</label></td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-window-open" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="globalHeatingModeSuspend" value="2" yaha="io_mode:write_change ; radio_target_pdi_tag:globalHeatingMode">
									        <label for="globalHeatingModeSuspend">$yaha_tuid:suspendforventilation$</label></td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-not-home" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="globalHeatingModeNotAtHome" value="3" yaha="io_mode:write_change ; radio_target_pdi_tag:globalHeatingMode">
									        <label for="globalHeatingModeNotAtHome">$yaha_tuid:notAtHomeFunction$</label></td>
							  			</tr>						

							  			<tr id="notAtHome_details_leaving">
							  				<td>$yaha_tuid:leaving$</td>
							  				<td>
							  					<input id="globalHeatingNotAtHomeStartDate" type="date" value="" yaha="io_mode:read_cyclic, write_change">$yaha_tuid:at$
							  					<input id="globalHeatingNotAtHomeStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change">
							  				</td>
							  			</tr>					  			
							  			<tr id="notAtHome_details_backhome">
							  				<td>$yaha_tuid:backhome$</td>
							  				<td>
							  					<input id="globalHeatingNotAtHomeEndDate" type="date" value="" yaha="io_mode:read_cyclic, write_change">$yaha_tuid:at$
							  					<input id="globalHeatingNotAtHomeEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change">
							  				</td>
							  			</tr>
							  		</tbody>
							  	</table>						        
						    </fieldset>
						</form>
						
					</div>
				</div>

			</div>

		</div>
		

		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:settings$ ;module_icon: yaha_settings">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:settings$</h1>
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel" data-role="collapsible" data-inset="false">
						<h3>$yaha_tuid:floorheating$</h3>

						<form id="form_floorheating_operating_mode">
					        <fieldset data-role="controlgroup">
								<table>	
									<tbody>						
							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-time" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="floorheatingmodeSelector" id="floorHeatingModeAuto" value="0" yaha="io_mode:write_change ; radio_target_pdi_tag:floorHeatingMode">
									        	<label for="floorHeatingModeAuto">$yaha_tuid:automaticoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="floorheatingmodeSelector" id="floorHeatingModeComfort" value="1" yaha="io_mode:write_change ; radio_target_pdi_tag:floorHeatingMode">
									        	<label for="floorHeatingModeComfort">$yaha_tuid:comfortoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-night" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="floorheatingmodeSelector" id="floorHeatingModeReduced" value="2" yaha="io_mode:write_change ; radio_target_pdi_tag:floorHeatingMode">
									        	<label for="floorHeatingModeReduced">$yaha_tuid:reducedoperation$</label>
									        </td>
							  			</tr>						

							  			<tr style="height:1em;"></tr>
							  		</tbody>
							  	</table>						        
						    </fieldset>
						</form>
						
						<hr>
						
						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5>$yaha_tuid:heatingphasesconfiguration$</td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:mondaytofriday$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="floorHeatingWeekdaysStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="floorHeatingWeekdaysEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:weekend$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="floorHeatingWeekendStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="floorHeatingWeekendEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>	
					  			
								<tr style="height:1em;"></tr>
					  								
					  		</tbody>
					  	</table>

						<hr>
						
						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5 style="width:400px">$yaha_tuid:reducedtemperature$ $yaha_tuid:lounge$</td>
					  			</tr>						
					  			<tr>
					  				<td style="width:120px">
										<span style="font-size:200%;" id="floorHeatingReducedTempSliderText"></span> <span style="font-size:200%;">&deg;C</span>							
									</td>
									<td colspan=4>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="18" 
										data-highlight="true" 
										id="floorHeatingReducedTemp" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: floorHeatingReducedTempSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
						</table>

						<hr>

						<table>	
							<tbody>						
					  			<tr>
					  				<td>
					  					<div class="rotate90left" style="width:30px"><span style="font-size:14px">$yaha_tuid:flowtemperature$</span></div>
					  				</td>
					  				<td colspan=2>
					  					<canvas id="canvasHeatcurveFloorHeating" width="300" height="300"></canvas>
					  				</td>
					  			</tr>

					  			<tr>
					  				<td>
					  				</td>
					  				<td  colspan=2 style="text-align:center">
					  					<span style="font-size:14px">$yaha_tuid:outtemperature$</span>
					  				</td>
								</tr>

					  			<tr>
					  				<td>
					  				</td>
					  				<td>
										$yaha_tuid:level$ <input type="number" step="1" style="width:40" id="floorHeatCurveLevel" yaha="io_mode:read_cyclic, write_change">
					  				</td>
					  				<td>
										$yaha_tuid:slope$ <input type="number" step="0.1" style="width:60" id="floorHeatCurveSlope" yaha="io_mode:read_cyclic, write_change">
					  				</td>
					  			</tr>
							</tbody>						
						</table>

					</div>
				</div>			

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel" data-role="collapsible" data-inset="false">
						<h3>$yaha_tuid:radiatorheating$</h3>

						<form id="form_radiatorheating_operating_mode">
					        <fieldset data-role="controlgroup">
								<table>	
									<tbody>						
							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-time" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="radiatorheatingmodeSelector" id="radiatorHeatingModeAuto" value="0" yaha="io_mode:write_change ; radio_target_pdi_tag:radiatorHeatingMode">
									        	<label for="radiatorHeatingModeAuto">$yaha_tuid:automaticoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="radiatorheatingmodeSelector" id="radiatorHeatingModeComfort" value="1" yaha="io_mode:write_change ; radio_target_pdi_tag:radiatorHeatingMode">
									        	<label for="radiatorHeatingModeComfort">$yaha_tuid:comfortoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-night" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="radiatorheatingmodeSelector" id="radiatorHeatingModeReduced" value="2" yaha="io_mode:write_change ; radio_target_pdi_tag:radiatorHeatingMode">
									        	<label for="radiatorHeatingModeReduced">$yaha_tuid:reducedoperation$</label>
									        </td>
							  			</tr>						

							  			<tr style="height:1em;"></tr>
							  		</tbody>
							  	</table>						        
						    </fieldset>
						</form>
						
						<hr>
						
						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5>$yaha_tuid:heatingphasesconfiguration$</td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:mondaytofriday$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="radiatorHeatingWeekdaysStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="radiatorHeatingWeekdaysEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:weekend$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="radiatorHeatingWeekendStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="radiatorHeatingWeekendEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>	
					  			
								<tr style="height:1em;"></tr>
					  								
					  		</tbody>
					  	</table>

						<hr>
						
						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5 style="width:400px">$yaha_tuid:reducedtemperature$ $yaha_tuid:library$</td>
					  			</tr>						
					  			<tr>
					  				<td style="width:120px">
										<span style="font-size:200%;" id="radiatorHeatingReducedTempSliderText"></span> <span style="font-size:200%;">&deg;C</span>							
									</td>
									<td colspan=4>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="18" 
										data-highlight="true" 
										id="radiatorHeatingReducedTemp" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: radiatorHeatingReducedTempSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
						</table>

						<hr>

						<table>	
							<tbody>						
					  			<tr>
					  				<td>
					  					<div class="rotate90left" style="width:30px"><span style="font-size:14px">$yaha_tuid:flowtemperature$</span></div>
					  				</td>
					  				<td colspan=2>
					  					<canvas id="canvasHeatcurveRadiatorHeating" width="300" height="300"></canvas>
					  				</td>
					  			</tr>

					  			<tr>
					  				<td>
					  				</td>
					  				<td  colspan=2 style="text-align:center">
					  					<span style="font-size:14px">$yaha_tuid:outtemperature$</span>
					  				</td>
								</tr>

					  			<tr>
					  				<td>
					  				</td>
					  				<td>
										$yaha_tuid:level$ <input type="number" step="1" style="width:40" id="radiatorHeatCurveLevel" yaha="io_mode:read_cyclic, write_change">
					  				</td>
					  				<td>
										$yaha_tuid:slope$ <input type="number" step="0.1" style="width:60" id="radiatorHeatCurveSlope" yaha="io_mode:read_cyclic, write_change">
					  				</td>
					  			</tr>
							</tbody>						
						</table>

					</div>
				</div>			


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel" data-role="collapsible" data-inset="false">
						<h3>$yaha_tuid:hotwatersupply$</h3>
						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5>$yaha_tuid:heatingphasesconfiguration$</td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:morning$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="hotwaterMorningStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="hotwaterMorningEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:evening$</td>
									<td>$yaha_tuid:from$</td>
									<td><input id="hotwaterEveningStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
									<td>$yaha_tuid:to$</td>
									<td><input id="hotwaterEveningEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_change"></td>
					  			</tr>						

							  	<tr style="height:1em;"></tr>

					  		</tbody>
					  	</table>


						<hr>
						
						<table>	
							<tbody>	
					  			<tr>
									<td style="width:170px">
										<span>$yaha_tuid:status$</span>
									</td>
									<td colspan=2>
										<span id="symbolHotwaterState" class="yaha-symbol yaha-symbol-weather-fire" style="width: 40px; line-height: 30px;"></span>
									</td>
					  			</tr>	

					  			<tr>
									<td colspan=3>$yaha_tuid:settemperature$</td>
					  			</tr>						

					  			<tr>
					  				<td style="width:120px">
										<span style="font-size:200%;" id="hotwaterSetTempSliderText"></span> <span style="font-size:200%;">&deg;C</span>							
									</td>
									<td colspan=2 style="width:300px">
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="70" 
										step="1.0" 
										value="60" 
										data-highlight="true" 
										id="hotwaterSetTemp" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: hotwaterSetTempSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>	

			</div>
		</div>
		

		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:charts$ ; module_icon: yaha_chart">
			<span style="font-size:14px; font-weight: bold; margin-left: 20px">$yaha_tuid:showyear$: </span><input style="text-align: right; width: 4em" type="number" id="yearLog">

			<div style="margin-top: 20px;"; id="statistics_linechart">
			<!-- filled by function -->
			</div>
		</div>


		
		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:manualoperation$ ;module_icon: yaha_hand">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:manualoperation$</h1>
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item" id="process_graphic_container">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:heatingcircuit$</h3>

						<table>	
							<tbody>	
					  			<tr>							
									<td>
										<object data="../yaha/core/svg/yaha_heating_circuit.svg" type="image/svg+xml" id="heatingCircuitSVG" style="width: 700px; line-height: 500px"></object>
									</td>
									
									<td style="vertical-align:top; padding-left: 60px">
									
										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:burner$</h4>
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="burnerManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'burnermanualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="burnermanualoperation">
										    		<tr>
										  				<td>$yaha_tuid:controllerrelease$</td>
					  									<td style="text-align:left">
					  										<input id="burnerManControllerRelease" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$">
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:settemperature$</td>
					  									<td style="text-align:left">
					  										<input id="burnerManSetTemp" yaha="io_mode:read_cyclic, write_change" type="number" step="1"; style="width:50">&deg;C
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:totaloperatinghours$</td>
					  									<td style="text-align:left">
															<span id="burnerTotalOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>					  										
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:annualoperatinghours$</td>
					  									<td style="text-align:left">
															<span id="burnerAnnualOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>					  										
										    			</td>
										    		</tr>
										    	</tbody>
										    </table>

										</div>	

										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:floorheatingpump$</h4>
										    
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="floorPumpManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'pumpfloormanualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="pumpfloormanualoperation">
										    		<tr>
										  				<td>$yaha_tuid:override$</td>
					  									<td style="text-align:left">
					  										<input id="floorPumpManOverride" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$">
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:totaloperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="floorPumpTotalOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:annualoperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="floorPumpAnnualOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>

							  						<tr style="height:1em;"></tr>
							  			
					  								<tr>
										  				<td colspan=2><span id="floorPumpAlarmFrostProtectEffect" class="blink" style="color:red;">$yaha_tuid:frostprotectionmodeactive$</span></td>
						  							</tr>						
					  								<tr>
										  				<td colspan=2><span id="floorPumpAlarmSafetyReleaseOffEffect" class="blink" style="color:red;">$yaha_tuid:safetyreleaseoff$</span></td>
						  							</tr>						
										    	</tbody>
										    </table>										    
										</div>	

										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:radiatorpump$</h4>
										    
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="radiatorPumpManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'pumpradiatormanualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="pumpradiatormanualoperation">
										    		<tr>
										  				<td>$yaha_tuid:override$</td>
					  									<td style="text-align:left">
					  										<input id="radiatorPumpManOverride" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$">
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:totaloperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="radiatorPumpTotalOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:annualoperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="radiatorPumpAnnualOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>

							  						<tr style="height:1em;"></tr>
							  			
					  								<tr>
										  				<td colspan=2><span id="radiatorPumpAlarmFrostProtectEffect" class="blink" style="color:red;">$yaha_tuid:frostprotectionmodeactive$</span></td>
						  							</tr>						
					  								<tr>
										  				<td colspan=2><span id="radiatorPumpAlarmSafetyReleaseOffEffect" class="blink" style="color:red;">$yaha_tuid:safetyreleaseoff$</span></td>
						  							</tr>						
										    	</tbody>
										    </table>										    
										</div>	

										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:hotwaterpump$</h4>
										    
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="hotwaterPumpManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'pumphotwatermanualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="pumphotwatermanualoperation">
										    		<tr>
										  				<td>$yaha_tuid:override$</td>
					  									<td style="text-align:left">
					  										<input id="hotwaterPumpManOverride" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$">
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:totaloperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="hotwaterPumpTotalOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>
										    		<tr>
										  				<td>$yaha_tuid:annualoperatinghours$</td>
					  									<td style="text-align:left">
					  										<span id="hotwaterPumpAnnualOperatingHours" yaha="io_mode:read_cyclic ; format:0.0 ; unit:h>h show">0</span>
										    			</td>
										    		</tr>
										    	</tbody>
										    </table>										    
										</div>	


										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:floorheatingroomcontroller$</h4>
										    
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="floorHeatingManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'roomcontrollerFloorHeatingManualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="roomcontrollerFloorHeatingManualoperation">
										    		<tr>
										  				<td>$yaha_tuid:mixersetposition$</td>
					  									<td style="text-align:left">
															<input id="floorHeatingMixerManSetPosition" yaha="io_mode:read_cyclic, write_change" type="number" step="1"; style="width:40"> %
										    			</td>
										    		</tr>
										    		
										    		<tr>
										  				<td>$yaha_tuid:mixerhoming$</td>
					  									<td style="text-align:left">
															<a href="#" id="floorMixerHoming" yaha="io_mode:write_click ; tag_group_wr_click:FLOOR_MIXER_HOMING" data-role="button" data-icon="home" data-mini="true" data-inline="true">$yaha_tuid:start$</a>
															<span style="visibility:hidden" id="floorHeatingMixerManHoming" yaha="tag_group:FLOOR_MIXER_HOMING">1</span>
										    			</td>
										    		</tr>
										    	</tbody>
										    </table>										    
										</div>	

										<div data-role="collapsible" data-mini="true" data-collapsed-icon="carat-d" data-expanded-icon="carat-u">
										    <h4>$yaha_tuid:radiatorheatingroomcontroller$</h4>
										    
										    <table>
										    	<thead>
										    		<tr>
										  				<th style="text-align:left; width: 200px">$yaha_tuid:manualoperation$</th>
					  									<th style="text-align:left">
					  										<input id="radiatorHeatingManOp" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$" onchange="tagEnableDisable(this.id, 'roomcontrollerRadiatorHeatingManualoperation')">
										    			</th>
										    		</tr>
												</thead>
										    	<tbody id="roomcontrollerRadiatorHeatingManualoperation">
										    		<tr>
										  				<td>$yaha_tuid:mixersetposition$</td>
					  									<td style="text-align:left">
															<input id="radiatorHeatingMixerManSetPosition" yaha="io_mode:read_cyclic, write_change" type="number" step="1"; style="width:40"> %
										    			</td>
										    		</tr>
										    		
										    		<tr>
										  				<td>$yaha_tuid:mixerhoming$</td>
					  									<td style="text-align:left">
															<a href="#" id="radiatorMixerHoming" yaha="io_mode:write_click ; tag_group_wr_click:RADIATOR_MIXER_HOMING" data-role="button" data-icon="home" data-mini="true" data-inline="true">$yaha_tuid:start$</a>
															<span style="visibility:hidden" id="radiatorHeatingMixerManHoming" yaha="tag_group:RADIATOR_MIXER_HOMING">1</span>
										    			</td>
										    		</tr>
										    	</tbody>
										    </table>										    
										</div>	


									</td>
									
								</tr>
							</tbody>
						</table>
					</div>	
				</div>

				<div class="yaha_flex_item" id="trend_chart_container">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:trend$</h3>

						<table>	
							<tbody>	
					  			<tr>							
									<td>
										<div style="margin-top: 20px;"; id="trend_chart">
											<!-- filled by function -->
										</div>									
									</td>
								</tr>
								<tr>
									<td style="vertical-align:top; padding-left: 40px">
									  	<a href="#" id="cmdRecorderStart" data-role="button" data-icon="video" data-mini="true" data-inline="true" style="display: inline-block; width: 80px" yaha="io_mode:write_click ; tag_group_wr_click:RECORDER_CMD_START">$yaha_tuid:start$</a>
									  	<a href="#" id="cmdRecorderStop" data-role="button" data-icon="forbidden" data-mini="true" data-inline="true" style="display: inline-block; width: 80px" yaha="io_mode:write_click ; tag_group_wr_click:RECORDER_CMD_STOP">$yaha_tuid:stop$</a>
									  	<a href="#" id="trendChartRefresh" data-role="button" data-icon="refresh" data-mini="true" data-inline="true" style="display: inline-block; width: 80px">$yaha_tuid:refresh$</a>
									  	<a href="#" id="cmdRecorderClear" data-role="button" data-icon="delete" data-mini="true" data-inline="true" style="display: inline-block; width: 80px" yaha="io_mode:write_click ; tag_group_wr_click:RECORDER_CMD_CLEAR">$yaha_tuid:clear$</a>
									</td>
								</tr>
							</tbody>
						</table>
					</div>	
				</div>

			</div>
		</div>

		<div id="yaha_submodule_5" class="yaha-submodule" yaha="module_name: $yaha_tuid:generalsettings$ ;module_icon: yaha_settings">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:settings$</h1>
			</div>
	
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div id="languageSelector" class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:languageselection$</h3>
					</div>	
				</div>
				
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:dateandtime$</h3>
						
						<table>
							<thead>
								<tr>
									<th></th>
									<th>$yaha_tuid:ondevice$</th>
									<th style="text-align:left; padding-left:10px">$yaha_tuid:new$</th>
								</tr>
							</thead>
							<tbody>						
					  			<tr>
			    					<td>$yaha_tuid:time$</td>
			    					<td style="padding-left: 15px"><span id="currentHour" yaha="io_mode:read_cyclic ; format:00"></span>:<span id="currentMinute" yaha="io_mode:read_cyclic ; format:00"></span>:<span id="currentSecond" yaha="io_mode:read_cyclic ; format:00"></span></td>
			    					<td style="padding-left: 10px"><input type="time" id="setTimeString" yaha="tag_group:DATETIME_SET" value=""></td>
			  					</tr>			
					  			<tr>
			    					<td>$yaha_tuid:date$</td>
			    					<td style="padding-left: 15px"><span id="currentDay" yaha="io_mode:read_cyclic ; format:00"></span>.<span id="currentMonth" yaha="io_mode:read_cyclic ; format:00"></span>.<span id="currentYear" yaha="io_mode:read_cyclic ; format:00"></span></td>
			    					<td style="padding-left: 10px"><input type="date" id="setDateString" yaha="tag_group:DATETIME_SET" value=""></td>
			  					</tr>	
			  					<tr>
			    					<td></td>
			    					<td></td>
			    					<td>
									  	<a href="#" data-role="button" data-icon="check" data-mini="true" data-inline="true" id="uicmdSetDateTime" yaha="io_mode:write_click ; tag_group_wr_click:DATETIME_SET">$yaha_tuid:apply$</a>
			    						<span style="visibility:hidden" id="cmdSetDateTime" yaha="tag_group:DATETIME_SET">1</span>
			    					</td>
			  					</tr>	
							</tbody>
						</table>					
					</div>	
					
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
					  	<table>
					  		<tbody>
					  			<tr>
					  				<td>$yaha_tuid:cycletime$</td>
					  				<td><span id="systemTickRunTime" yaha="io_mode:read_cyclic ; format:00.## ; unit:s>ms show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:cpuload$</td>
					  				<td><span id="cpuLoad" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>% show">tbd...</span></td>
					  			</tr>
					  			<tr>
									<td colspan="2">
									  	<a href="#" data-role="button" data-mini="true" data-inline="true" id="stopSystem" yaha="io_mode:write_click ; tag_group_wr_click:STOP_SYSTEM">Stop Yaha System</a>
										<span style="visibility:hidden" id="cmdStopSystem" yaha="tag_group:STOP_SYSTEM">1</span>
									</td>
					  			</tr>
					  		</tbody>
					  	</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
				  		<h2 style="text-align:left">PDI Monitor</h2>
				  	
						<table id="pdi_monitor" cellspacing="0" width="40%" border=1>
						  <tr>
						    <th><input class='pdi_mon_check_all' type='checkbox' onclick="pdi_mon_select_all_tags()"/></th>
						    <th>Tag Name</th>
						    <th>Tag Value</th>
						  </tr>
						</table>
					</div>
				  	<div>
						<a href="#" data-role="button" data-icon="minus" data-mini="true" data-inline="true" id="pdi_mon_delete_tag">Delete</a>
						<a href="#" data-role="button" data-icon="plus" data-mini="true" data-inline="true" id="pdi_mon_add_tag">Add</a>
					</div>					
				</div>					




			</div>
	
			<div style="visibility:hidden">
			  	<!-- the following line stores the flags used to send button trigger to server -->
			</div>
			
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

