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
			
			/* dynamic display of holiday parameters /Begin */
			//show or hide on load
			if ($('input[name=heatingmode]:checked', '#form_operating_mode').val() == 'holiday')
			{
				$("#onholiday_details_leaving").show()
				$("#onholiday_details_backhome").show()			
			}
			else
			{
				$("#onholiday_details_leaving").hide()
				$("#onholiday_details_backhome").hide()			
			}

			//show or hide on if selected or deselected
			$('#form_operating_mode input').on('change', function() 
														{
															if ($('input[name=heatingmode]:checked', '#form_operating_mode').val() == 'holiday')
															{
																$("#onholiday_details_leaving").show()
																$("#onholiday_details_backhome").show()			
															}
															else
															{
																$("#onholiday_details_leaving").hide()
																$("#onholiday_details_backhome").hide()			
															}
														});
			/* dynamic display of holiday parameters /End */
			
		</script>
		
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
										<span>20</span> <span>&deg;C</span>
									</td>
									<td>
										<span class="yaha-symbol yaha-symbol-switched-on" style="width: 40px; line-height: 30px;"></span>
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
										<span style="font-size:300%;" id="setTempRoomLoungeSliderText"></span> <span style="font-size:300%;">&deg;C</span>							
									</td>
									<td colspan=2>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										id="setTempRoomLounge" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: setTempRoomLoungeSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>
			</div>
			
			<div class="yaha_flex_container">
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
										<span>19</span> <span>&deg;C</span>
									</td>
									<td>
										<span class="yaha-symbol yaha-symbol-switched-on" style="width: 40px; line-height: 30px;"></span>
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
										<span style="font-size:300%;" id="setTempRoomLibrarySliderText"></span> <span style="font-size:300%;">&deg;C</span>							
									</td>
									<td colspan=2>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										id="setTempRoomLibrary" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: setTempRoomLibrarySliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>
			</div>			


			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:alarmmessages$</h3>

						<table style="display:none">	
							<tbody>						
					  			<tr>
					  				<td><span style="color:green;">$yaha_tuid:noalarmspending$</span></td>
					  			</tr>						
					  			<tr>
					  				<td><span class="blink" style="color:red;">$yaha_tuid:burnerovertemperatur$</span></td>
					  			</tr>						
					  			<tr>
					  				<td><span class="blink" style="color:red;">$yaha_tuid:burnerfault$</span></td>
					  			</tr>
					  			<tr>
					  				<td><span class="blink" style="color:red;">$yaha_tuid:frostprotection$</span></td>
					  			</tr>
					  		</tbody>
					  	</table>				
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
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:heatingmode$</h3>

						<form id="form_operating_mode">
					        <fieldset data-role="controlgroup">
								<table>	
									<tbody>						
							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-switched-on" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="id_op_mode_switched_on" value="on" checked="checked">
									        <label for="id_op_mode_switched_on">$yaha_tuid:switchedon$</label></td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-heating-off" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="id_op_mode_switched_off" value="off">
									        <label for="id_op_mode_switched_off">$yaha_tuid:switchedoff$</label></td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center"><span class="yaha-symbol yaha-symbol-not-home" style="width: 40px; line-height: 30px;"></span></td>
									        <td><input type="radio" name="heatingmode" id="id_op_mode_holiday" value="holiday">
									        <label for="id_op_mode_holiday">$yaha_tuid:holidayfunction$</label></td>
							  			</tr>						


							  			<tr id="onholiday_details_leaving">
							  				<td>$yaha_tuid:leaving$</td>
							  				<td><input type="date" value=""></input>$yaha_tuid:at$<input type="time" value=""></input></td>
							  			</tr>					  			
							  			<tr id="onholiday_details_backhome">
							  				<td>$yaha_tuid:backhome$</td>
							  				<td><input type="date" value=""></input>$yaha_tuid:at$<input type="time" value=""></input></td>
							  			</tr>
							  		</tbody>
							  	</table>						        
						    </fieldset>
						</form>
						
					</div>
				</div>
			</div>


			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
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
									        	<input type="radio" name="floorheatingmode" id="id_floorheating_mode_time" value="time" checked="checked">
									        	<label for="id_floorheating_mode_time">$yaha_tuid:automaticoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="floorheatingmode" id="id_floorheating_mode_comfort" value="time">
									        	<label for="id_floorheating_mode_comfort">$yaha_tuid:comfortoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-night" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="floorheatingmode" id="id_floorheating_mode_eco" value="time">
									        	<label for="id_floorheating_mode_eco">$yaha_tuid:reducedoperation$</label>
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
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:weekend$</td>
									<td>$yaha_tuid:from$</td>
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
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
										<span style="font-size:300%;" id="setReducedTempRoomLoungeSliderText"></span> <span style="font-size:300%;">&deg;C</span>							
									</td>
									<td colspan=4>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										id="setTempRoomLounge" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: setReducedTempRoomLoungeSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
						</table>
					</div>
				</div>			
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
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
									        	<input type="radio" name="radiatorheatingmode" id="id_radiatorheating_mode_time" value="time" checked="checked">
									        	<label for="id_radiatorheating_mode_time">$yaha_tuid:automaticoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-weather-sun" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="radiatorheatingmode" id="id_radiatorheating_mode_comfort" value="time">
									        	<label for="id_radiatorheating_mode_comfort">$yaha_tuid:comfortoperation$</label>
									        </td>
							  			</tr>						

							  			<tr>
											<td style="text-align:center">
												<span class="yaha-symbol yaha-symbol-night" style="width: 40px; line-height: 30px;"></span>
											</td>
									        <td>
									        	<input type="radio" name="radiatorheatingmode" id="id_radiatorheating_mode_eco" value="time">
									        	<label for="id_radiatorheating_mode_eco">$yaha_tuid:reducedoperation$</label>
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
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:weekend$</td>
									<td>$yaha_tuid:from$</td>
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
					  			</tr>						

							  	<tr style="height:1em;"></tr>

					  		</tbody>
					  	</table>

						<hr>
						
						<table>	
							<tbody>	
					  			<tr>
									<td colspan=2 style="width:400px">$yaha_tuid:reducedtemperature$ $yaha_tuid:library$</td>
					  			</tr>						
					  			<tr>
					  				<td style="width:120px">
										<span style="font-size:300%;" id="setReducedTempRoomLibrarySliderText"></span> <span style="font-size:300%;">&deg;C</span>							
									</td>
									<td>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="30" 
										step="1.0" 
										value="21" 
										data-highlight="true" 
										id="setTempRoomLounge" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: setReducedTempRoomLibrarySliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>			
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:hotwatersupply$</h3>

						<table>	
							<tbody>						
					  			<tr>
									<td colspan=5>$yaha_tuid:heatingphasesconfiguration$</td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:morning$</td>
									<td>$yaha_tuid:from$</td>
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
					  			</tr>						

					  			<tr>						
									<td>$yaha_tuid:evening$</td>
									<td>$yaha_tuid:from$</td>
									<td><input type="time" value=""></td>
									<td>$yaha_tuid:to$</td>
									<td><input type="time" value=""></td>
					  			</tr>						

							  	<tr style="height:1em;"></tr>

					  		</tbody>
					  	</table>

						<hr>
						
						<table>	
							<tbody>	
					  			<tr>
									<td colspan=2 style="width:400px">
										<span>$yaha_tuid:acttemperature$ $yaha_tuid:boiler$</span> <span>65</span> <span>&deg;C</span>
										<span class="yaha-symbol yaha-symbol-fire" style="width: 40px; line-height: 30px;"></span>
									</td>
					  			</tr>	

					  			<tr>
									<td colspan=2 style="width:400px">$yaha_tuid:settemperature$ $yaha_tuid:boiler$</td>
					  			</tr>						
					  			<tr>
					  				<td style="width:120px">
										<span style="font-size:300%;" id="setHotwaterTemperatureSliderText"></span> <span style="font-size:300%;">&deg;C</span>							
									</td>
									<td>
										<input 
										type="number" 
										data-type="range" 
										min="10" 
										max="70" 
										step="1.0" 
										value="60" 
										data-highlight="true" 
										id="setTempRoomLounge" 
										yaha="io_mode:read_cyclic, write_change ; mirror_span_id: setHotwaterTemperatureSliderText">							
					  				</td>
					  			</tr>
					  		</tbody>
					  	</table>

					</div>
				</div>			
			</div>

		</div>
		


		
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:manualoperation$ ;module_icon: yaha_hand">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:diagnostics$</h1>
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:temperatures$</h3>
						
						<table>	
							<tbody>						
					  			<tr>
					  				<td>$yaha_tuid:flowradiator$</td>
					  				<td style="padding-left: 15px"><span id="ioRawTempFlowRadiator" yaha="io_mode:read_cyclic ; format:0">tbd...</span> Ohm</td>
					  				<td style="padding-left: 15px"><span id="actTempFlowRadiator" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:flowfloor$</td>
					  				<td style="padding-left: 15px"><span id="ioRawTempFlowFloor" yaha="io_mode:read_cyclic ; format:0">tbd...</span> Ohm</td>
					  				<td style="padding-left: 15px"><span id="actTempFlowFloor" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:northside$</td>
					  				<td style="padding-left: 15px"><span id="ioRawTempOutsideNorth" yaha="io_mode:read_cyclic ; format:0">tbd...</span> Ohm</td>
					  				<td style="padding-left: 15px"><span id="actTempOutsideNorth" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:boiler$</td>
					  				<td style="padding-left: 15px"><span id="ioRawTempBoiler" yaha="io_mode:read_cyclic ; format:0">tbd...</span> Ohm</td>
					  				<td style="padding-left: 15px"><span id="actTempBoiler" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:lounge$</td>
					  				<td colspan=2 style="padding-left: 15px"><span id="actTempRoomLounge" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:settemperature$</td>
					  			</tr>
					  		</tbody>							
						</table>
					</div>
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:burner$</h3>
						
						<table>	
							<tbody>						
					  			<tr>
					  				<td>$yaha_tuid:acttemperature$</td>
					  				<td style="padding-left: 15px"><span id="ioRawTempBurner" yaha="io_mode:read_cyclic ; format:0">tbd...</span> Ohm</td>
					  				<td style="padding-left: 15px"><span id="actTempBurner" yaha="io_mode:read_cyclic ; format:0.# ; unit:$deg$C>$deg$C show">tbd...</span></td>
					  			</tr>

					  			<tr>
					  				<td>$yaha_tuid:settemperature$</td>
					  				<td colspan=2 style="padding-left: 15px"><input type="text" id="setTempBurner" yaha="io_mode:read_cyclic, write_enter"></span></td>
					  			</tr>

					  			<tr>
					  				<td>$yaha_tuid:release$</td>
					  				<td colspan=2 style="padding-left: 15px"></span><input type="checkbox" id="ioBurnerRelease" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>

					  			<tr>
					  				<td>$yaha_tuid:status$</td>
					  				<td colspan=2 style="padding-left: 15px"><span id="ioBurnerSwitchedOn" yaha="io_mode:read_cyclic; value_map:1=$yaha_tuid:on$,0=$yaha_tuid:off$">tbd...</span></td>
					  			</tr>

					  			<tr>
					  				<td>$yaha_tuid:failure$</td>
					  				<td colspan=2 style="padding-left: 15px"><span id="ioBurnerFailure" yaha="io_mode:read_cyclic; value_map:1=$yaha_tuid:yes$,0=$yaha_tuid:no$">tbd...</span></td>
					  			</tr>

					  			<tr>
					  				<td>$yaha_tuid:overtemperature$</td>
					  				<td colspan=2 style="padding-left: 15px"><span id="ioBurnerOvertemperature" yaha="io_mode:read_cyclic; value_map:1=$yaha_tuid:yes$,0=$yaha_tuid:no$">tbd...</span></td>
					  			</tr>
					  		</tbody>							
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:pumps$</h3>
						
						<table>	
							<tbody>						
					  			<tr>
					  				<td>$yaha_tuid:flowradiator$</td>
					  				<td colspan=2 style="padding-left: 15px"></span><input type="checkbox" id="ioPumpRadiator" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:flowfloor$</td>
					  				<td colspan=2 style="padding-left: 15px"></span><input type="checkbox" id="ioPumpFloor" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:boiler$</td>
					  				<td colspan=2 style="padding-left: 15px"></span><input type="checkbox" id="ioPumpBoiler" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>
					  		</tbody>							
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:mixers$</h3>
						
						<table>	
							<thead>
								<tr>
									<th></th>
									<th>$yaha_tuid:open$</th>
									<th>$yaha_tuid:close$</th>
								</tr>
							</thead>
							<tbody>						
					  			<tr>
					  				<td>$yaha_tuid:flowradiator$</td>
					  				<td style="padding-left: 15px"></span><input type="checkbox" id="ioFlowMixerRadiatorOpen" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  				<td style="padding-left: 15px"></span><input type="checkbox" id="ioFlowMixerRadiatorClose" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:flowfloor$</td>
					  				<td style="padding-left: 15px"></span><input type="checkbox" id="ioFlowMixerFloorOpen" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  				<td style="padding-left: 15px"></span><input type="checkbox" id="ioFlowMixerFloorClose" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
					  			</tr>
					  		</tbody>							
						</table>
					</div>
				</div>			
			
			</div>
		</div>

		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:generalsettings$ ;module_icon: yaha_settings">
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
	
			<div style="visibility:hidden">
			  	<!-- the following line stores the flags used to send button trigger to server -->
			</div>
			
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

