<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>overview</id>
		<name>$yaha_tuid:myhome$</name>
		<order>0</order>
		<icon>yaha_home</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			var cgiData = {}
			var INDEX_DAY = 0
			var INDEX_MONTH = 1
			var INDEX_YEAR = 2
			var INDEX_HOUR = 3
			var INDEX_MINUTE = 4
			var INDEX_SECOND = 5
				
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
			
		</script>
		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:dashboard$ ; module_icon: yaha_dashboard; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:dashboard$</h1>
			</div>
			

			<div class="yaha_flex_container">
				
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:allblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td>
										<span>$yaha_tuid:groundfloor$</span>
									</td>
									<td style="padding-left: 1em"><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGroundFloorBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:GROUND_FLOOR_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGroundFloorBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:GROUND_FLOOR_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGroundFloorBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:GROUND_FLOOR_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td>
										<span>$yaha_tuid:firstfloor$</span>
									</td>
									<td style="padding-left: 1em"><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdFirstFloorBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:FIRST_FLOOR_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdFirstFloorBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:FIRST_FLOOR_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdFirstFloorBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:FIRST_FLOOR_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
							</tbody>
						</table>						
					</div>
				</div>
				
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:outside$</h3>
						<table>
							<tbody>
								<tr>
									<td>
										<span>$yaha_tuid:acttemp$</span>
									</td>
									<td style="padding-left: 1em">
										<span id="actTempOutdoorWS1" yaha="io_mode:read_cyclic ; format:0.0 ; unit:$deg$C>$deg$C show">tbd...</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>				

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:lounge$</h3>
						<table>
							<tbody>
								<tr>
									<td>
										<span>$yaha_tuid:acttemp$</span>
									</td>
									<td style="padding-left: 1em">
										<span id="actTempIndoorWS1" yaha="io_mode:read_cyclic ; format:0.0 ; unit:$deg$C>$deg$C show">tbd...</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>				
				
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:library$</h3>
						<table>
							<tbody>
								<tr>
									<td>
										<span>$yaha_tuid:acttemp$</span>
									</td>
									<td style="padding-left: 1em">
										<span id="ioActTempLivingroom" yaha="io_mode:read_cyclic ; format:0.0 ; unit:$deg$C>$deg$C show">tbd...</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>				
				
				
			</div>
		</div>
		
		
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:diagnostics$ ;module_icon: yaha_debug">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:diagnostics$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
				  	<table>
				  		<tbody>
				  			<tr>
				  				<td>$yaha_tuid:livecounter$</td>
				  				<td><input type="text" id="count1" yaha="io_mode:read_cyclic, write_enter" class="count_field"></td>
				  			</tr>
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
		
		</div>
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:settings$ ;module_icon: yaha_settings">
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


			</div>
	
			<div style="visibility:hidden">
			  	<!-- the following line stores the flags used to send button trigger to server -->
				<span id="groundFloorBlindOpen" yaha="tag_group:GROUND_FLOOR_BLIND_OPEN">1</span>
				<span id="groundFloorBlindClose" yaha="tag_group:GROUND_FLOOR_BLIND_CLOSE">1</span>
				<span id="groundFloorBlindStop" yaha="tag_group:GROUND_FLOOR_BLIND_STOP">1</span>
				<span id="firstFloorBlindOpen" yaha="tag_group:FIRST_FLOOR_BLIND_OPEN">1</span>
				<span id="firstFloorBlindClose" yaha="tag_group:FIRST_FLOOR_BLIND_CLOSE">1</span>
				<span id="firstFloorBlindStop" yaha="tag_group:FIRST_FLOOR_BLIND_STOP">1</span>
			</div>
			
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

