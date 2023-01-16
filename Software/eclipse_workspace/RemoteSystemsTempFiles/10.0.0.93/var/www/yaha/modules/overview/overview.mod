<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>overview</id>
		<name>$yaha_tuid:alarmcenter$</name>
		<order>0</order>
		<icon>yaha_alarm</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			LOG_PATH             = "yaha/logs/"
			LOG_FILE_NAME_SUFFIX = ".csv"
			TREND_FILE_NAME_TRUNK  = "security"
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
				
				//set up PDI monitor just a bit once everything is loaded to avoid funny interference with jQuery!?
				setTimeout(pdiMonitorInit, 100)
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
			
			
			function handleAlarmCenterStateChange(id)
			{
				console.log($('#'+id).text())
				if ($('#'+id).text() == 2)
				{
					$('#alarmCenterStateDisarmed').hide()
					$('#alarmCenterStateToBeArmed').hide()
					$('#armCountDown').hide()
					$('#alarmCenterStateArmed').show()
					console.log("armed")
				}
				else if ($('#'+id).text() == 1)
				{
					$('#alarmCenterStateDisarmed').hide()
					$('#alarmCenterStateToBeArmed').show()
					$('#armCountDown').show()
					$('#alarmCenterStateArmed').hide()
					console.log("armed soon")
				}
				else
				{
					$('#alarmCenterStateDisarmed').show()
					$('#alarmCenterStateToBeArmed').hide()
					$('#armCountDown').hide()
					$('#alarmCenterStateArmed').hide()
					console.log("disarmed")
				}
				
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
			<span id="zoneStateEntrance" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:symbolZoneStateEntrance ; anim_svg_item_id:innercircle ; anim_attribute:style,fill ; anim_attr_val_map:0=#a5a5a5,1=#00b050,2=#ff0000"></span>
			<span id="zoneStateLounge" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:symbolZoneStateLounge ; anim_svg_item_id:innercircle ; anim_attribute:style,fill ; anim_attr_val_map:0=#a5a5a5,1=#00b050,2=#ff0000"></span>
			<span id="zoneStateBasement" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:symbolZoneStateBasement ; anim_svg_item_id:innercircle ; anim_attribute:style,fill ; anim_attr_val_map:0=#a5a5a5,1=#00b050,2=#ff0000"></span>
			<span id="zoneStateGarage" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:symbolZoneStateGarage ; anim_svg_item_id:innercircle ; anim_attribute:style,fill ; anim_attr_val_map:0=#a5a5a5,1=#00b050,2=#ff0000"></span>
			<span id="zoneStateFirstFloor" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:symbolZoneStateFirstFloor ; anim_svg_item_id:innercircle ; anim_attribute:style,fill ; anim_attr_val_map:0=#a5a5a5,1=#00b050,2=#ff0000"></span>

			<span id="alarmCenterMode" style="visibility:hidden" yaha="io_mode:read_cyclic; radio_map:0=alarmCenterModeManual,1=alarmCenterModeAutomatic"></span>
			<span id="alarmCenterState" class="blink" style="color:red; display:inline; font-size:20px; font-weight:bold" yaha="io_mode:read_cyclic" onchange="handleAlarmCenterStateChange(this.id)"></span>
		</div>	


		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:dashboard$ ; module_icon: yaha_dashboard; visible: onload">
			<div class="yaha_flex_header" style="text-align:center">
				<h1 style="text-align:center">$yaha_tuid:dashboard$</h1>
				<span id="alarmCenterStateDisarmed" style="display:none; color:#00b050; font-size:20px; font-weight:bold">$yaha_tuid:disarmed$</span>
				<span id="alarmCenterStateToBeArmed" class="blink" style="display:none; color:#FFA500; font-size:20px; font-weight:bold">$yaha_tuid:armedin$</span>
				<span id="alarmCenterStateArmed" class="blink" style="display:none; color:#ff0000; font-size:20px; font-weight:bold">$yaha_tuid:armed$</span>
				<span id="armCountDown" class="blink" style="display:none; color:#FFA500; font-size:20px; font-weight:bold" yaha="io_mode:read_cyclic ; format:00 ; unit:s>s show"></span>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:alarmoverview$</h3>
						<table>
							<tbody>
								<tr>
									<td style="width: 100px">$yaha_tuid:entrance$</td>
									<td><object data="../yaha/core/svg/symbol_circle.svg" type="image/svg+xml" id="symbolZoneStateEntrance" style="width: 40px; line-height: 30px"></object></td>
									<td style="width: 100px; text-align:right"><input id="zoneEnableEntrance" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>
								</tr>
								<tr>
									<td style="width: 100px">$yaha_tuid:lounge$</td>
									<td><object data="../yaha/core/svg/symbol_circle.svg" type="image/svg+xml" id="symbolZoneStateLounge" style="width: 40px; line-height: 30px"></object></td>
									<td style="width: 100px; text-align:right"><input id="zoneEnableLounge" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>
								</tr>
								<tr>
									<td style="width: 100px">$yaha_tuid:basement$</td>
									<td><object data="../yaha/core/svg/symbol_circle.svg" type="image/svg+xml" id="symbolZoneStateBasement" style="width: 40px; line-height: 30px"></object></td>
									<td style="width: 100px; text-align:right"><input id="zoneEnableBasement" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>
								</tr>
								<tr>
									<td style="width: 100px">$yaha_tuid:garage$</td>
									<td><object data="../yaha/core/svg/symbol_circle.svg" type="image/svg+xml" id="symbolZoneStateGarage" style="width: 40px; line-height: 30px"></object></td>
									<td style="width: 100px; text-align:right"><input id="zoneEnableGarage" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>
								</tr>
								<tr>
									<td style="width: 100px">$yaha_tuid:firstfloor$</td>
									<td><object data="../yaha/core/svg/symbol_circle.svg" type="image/svg+xml" id="symbolZoneStateFirstFloor" style="width: 40px; line-height: 30px"></object></td>
									<td style="width: 100px; text-align:right"><input id="zoneEnableFirstFloor" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:panicbutton$</h3>
						<a href="#" id="cmdButtonAlarmLight" yaha="io_mode:write_click ; tag_group_wr_click:BUTTON_ALARM_LIGHT" data-role="button" data-icon="alert" data-mini="true" data-inline="true">$yaha_tuid:flashlight$</a>
						<span style="visibility:hidden" id="uiButtonAlarmLight" yaha="tag_group:BUTTON_ALARM_LIGHT">1</span>
						
						<a href="#" id="cmdButtonAlarmSound" yaha="io_mode:write_click ; tag_group_wr_click:BUTTON_ALARM_SOUND" data-role="button" data-icon="audio" data-mini="true" data-inline="true">$yaha_tuid:sirene$</a>
						<span style="visibility:hidden" id="uiButtonAlarmSound" yaha="tag_group:BUTTON_ALARM_SOUND">1</span>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:alarmcenter$</h3>

						<a href="#" id="cmdButtonAlarmOff" yaha="io_mode:write_click ; tag_group_wr_click:BUTTON_ALARM_OFF" data-role="button" data-icon="check" data-mini="true" data-inline="true" style="color:red">$yaha_tuid:switchoffalarm$</a>
						<span style="visibility:hidden" id="uiButtonAlarmOff" yaha="tag_group:BUTTON_ALARM_OFF">1</span>


						<form id="form_operating_mode">
					        <fieldset data-role="controlgroup">
								<table>	
									<tbody>						
							  			<tr>
									        <td colspan=2><input type="radio" name="alarmcentermode" id="alarmCenterModeManual" value="0" yaha="io_mode:write_change ; radio_target_pdi_tag:alarmCenterMode">
									        <label for="alarmCenterModeManual">$yaha_tuid:manualoperation$</label></td>
							  			</tr>						
							  			<tr>
									        <td colspan=2><input type="radio" name="alarmcentermode" id="alarmCenterModeAutomatic" value="1" yaha="io_mode:write_change ; radio_target_pdi_tag:alarmCenterMode">
									        <label for="alarmCenterModeAutomatic">$yaha_tuid:automaticoperation$</label></td>
							  			</tr>						

							  			<tr>
											<td>$yaha_tuid:manual$</td>
											<td style="width: 100px; text-align:left"><input id="manuallyArmed" yaha="io_mode:read_cyclic, write_change" type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></td>

							  			</tr>	
							  			<tr>
											<td style="width: 140px">$yaha_tuid:armedat$</td>
											<td><input id="automaticArmStartTime" type="time" value="" yaha="io_mode:read_cyclic, write_blur"></td>
							  			</tr>	
							  			<tr>
											<td style="width: 140px">$yaha_tuid:disarmedfrom$</td>
											<td><input id="automaticArmEndTime" type="time" value="" yaha="io_mode:read_cyclic, write_blur"></td>
							  			</tr>
							  		</tbody>
							  	</table>						        
						    </fieldset>
						</form>
					</div>
				</div>
				
			</div>

		</div>
		

		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:generalsettings$ ;module_icon: yaha_settings">
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
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

