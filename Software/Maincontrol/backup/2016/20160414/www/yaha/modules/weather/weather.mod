<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>weather</id>
		<name>$yaha_tuid:weather$</name>
		<order>20</order>
		<icon>yaha_weather</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			WEATHER_LOG_PATH             = "yaha/logs/"
			WEATHER_LOG_FILE_NAME_TRUNK  = "weather_"
			WEATHER_LOG_FILE_NAME_SUFFIX = ".csv"
			
			function moduleInit()
			{
				var currentDate = new Date();
				var currentYear = currentDate.getFullYear();
				
				//set input field to current year
				$("#yearLog").val(currentYear)

				fileName = WEATHER_LOG_PATH + WEATHER_LOG_FILE_NAME_TRUNK + currentYear + WEATHER_LOG_FILE_NAME_SUFFIX
				drawLineChart("weather_linechart", fileName, "actTempOutdoor", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15)

				//add event in case year has been updated
				$(document).on("keypress", "#yearLog",
					function(event)
					{
						//console.log(event)

						var keycode = (event.keyCode ? event.keyCode : event.which);	//compatibility: use event.which if keyCode does not exists
						if (keycode == '13')	//enter key
						{
							fileName = WEATHER_LOG_PATH + WEATHER_LOG_FILE_NAME_TRUNK + $("#yearLog").val() + WEATHER_LOG_FILE_NAME_SUFFIX
							drawLineChart("weather_linechart", fileName, "actTempOutdoor", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15)
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
						fileName = WEATHER_LOG_PATH + WEATHER_LOG_FILE_NAME_TRUNK + $("#yearLog").val() + WEATHER_LOG_FILE_NAME_SUFFIX
						drawLineChart("weather_linechart", fileName, "actTempOutdoor", "%Y.%m.%d %H:%M:%S", "%d %b %H:%M", "", 15)
					});			
			}
			
			
			
		</script>

	  	<!-- the following line stores the flags used to send button trigger to server -->
		<div style="visibility:hidden">
			<span id="weatherConditionWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolweatherConditionWS1 ; symbol_map:0=yaha-symbol-weather-sun,1=yaha-symbol-weather-cloud-sun,2=yaha-symbol-weather-cloud,3=yaha-symbol-weather-rain,4=yaha-symbol-weather-snow"></span>
			<span id="actTempOutdoorTrendWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolOutdoorTempTrendWS1 ; symbol_map:-1=yaha-symbol-arrow-down-right,1=yaha-symbol-arrow-up-right"></span>
			<span id="actHumidityOutdoorTrendWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolOutdoorHumidityTrendWS1 ; symbol_map:-1=yaha-symbol-arrow-down-right,1=yaha-symbol-arrow-up-right"></span>
			<span id="relativePressureTrendWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolRelativePressureTrendWS1 ; symbol_map:-1=yaha-symbol-arrow-down-right,1=yaha-symbol-arrow-up-right"></span>
			<span id="uvRadiationIndexTrendWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; symbol_target_id:symbolUvRadiationIndexTrendWS1 ; symbol_map:-1=yaha-symbol-arrow-down-right,1=yaha-symbol-arrow-up-right"></span>
			<span id="windDirectionWS1" style="visibility:hidden" yaha="io_mode:read_cyclic ; anim_target_id:windDirAnimationWS1 ; anim_svg_item_id:winddir ; anim_attribute:transform,rotate ; anim_attr_val_min:0 ; anim_attr_val_max:360 ; anim_val_min:0 ; anim_val_max:360"></span>
		</div>	

		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:gardensouth$ ; module_icon: yaha_garden ; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:gardensouth$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:weathercondition$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="2">
										<span id="symbolweatherConditionWS1" class="yaha-symbol yaha-symbol-weather-sun" style="width: 150px; line-height: 100px;"></span>
									</td>
									<td>
										<span id="actTempOutdoorWS1" style="font-size:50px; vertical-align:middle; text-align:center" yaha="io_mode:read_cyclic ; format:0.0">tbd...</span><span style="font-size:30px; vertical-align:top; text-align:center"> &#8451;</span>
									</td>
									<td style="width: 50px">
										<span id="symbolOutdoorTempTrendWS1" class="yaha-symbol" style="width: 50px; line-height: 30px;"></span>
									</td>
								</tr>
								<tr>
									<td style="text-align:center">
										$yaha_tuid:feelslike$ <span id="actTempOutdoorFeelsLikeWS1" yaha="io_mode:read_cyclic ; format:0.0 ; unit:$deg$C>$deg$C show">tbd...</span>
									</td>
									<td>
									</td>
								</tr>

								<tr>
									<td colspan="3" style="padding-top: 1em"></td>
								</tr>

								<tr>
									<td style="padding-top: 0.7em">
										$yaha_tuid:humidity$
									</td>
									<td style="padding-top: 0.7em; text-align:right">
										<span id="actHumidityOutdoorWS1" yaha="io_mode:read_cyclic">tbd...</span> %
									</td>
									<td  style="padding-top: 0.7em; width: 50px;>
										<span id="symbolOutdoorHumidityTrendWS1" class="yaha-symbol" style="width: 50px; line-height: 30px;"></span>
									</td>
								</tr>
								<tr>
									<td style="padding-top: 0.7em">
										$yaha_tuid:pressure$
									</td>
									<td style="padding-top: 0.7em; text-align:right">
										<span id="relativePressureWS1" yaha="io_mode:read_cyclic">tbd...</span> hPa
									</td>
									<td  style="padding-top: 0.7em; width: 50px">
										<span id="symbolRelativePressureTrendWS1" class="yaha-symbol" style="width: 50px; line-height: 30px;"></span>
									</td>
								</tr>
								<tr>
									<td style="padding-top: 0.7em">
										$yaha_tuid:uvindex$
									</td>
									<td style="padding-top: 0.7em; text-align:right">
										<span id="uvRadiationIndexWS1" yaha="io_mode:read_cyclic">tbd...</span> $yaha_tuid:of$ 10
									</td>
									<td  style="padding-top: 0.7em; width: 50px">
										<span id="symbolUvRadiationIndexTrendWS1" class="yaha-symbol" style="width: 50px; line-height: 30px;"></span>
									</td>
								</tr>
								<tr>
									<td style="padding-top: 0.7em">
										$yaha_tuid:rain$
									</td>
									<td colspan=2 style="padding-top: 0.7em; text-align:right">
										<span id="rainHourlyWS1" yaha="io_mode:read_cyclic">tbd...</span> $yaha_tuid:mmperhour$
									</td>
								</tr>
								
								
							</tbody>
						</table>
					</div>
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:wind$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="2">
										<object data="../yaha/core/svg/symbol_compass_rose_wind.svg" type="image/svg+xml" id="windDirAnimationWS1"></object>
									</td>
									<td  style="padding-left: 1.5em">
										<span id="windSpeedWS1" style="font-size:50px; vertical-align:middle; text-align:center" yaha="io_mode:read_cyclic ; format:0.0">tbd...</span><span style="font-size:30px; vertical-align:top; text-align:center"> km/h</span>
									</td>
								</tr>
								<tr>
									<td style="text-align:center">
										$yaha_tuid:gust$ <span id="windGustWS1" yaha="io_mode:read_cyclic ; format:0.0 ; unit:km/h>km/h show">tbd...</span>
									</td>
								</tr>


							</tbody>
						</table>
					</div>
				</div>

			</div>
		</div>

		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:charts$ ; module_icon: yaha_chart">
			<span style="font-size:14px; font-weight: bold; margin-left: 20px">$yaha_tuid:showyear$: </span><input style="text-align: right; width: 4em" type="number" id="yearLog">

			<div style="margin-top: 20px"; id="weather_linechart">
			<!-- filled by function -->
			</div>
		</div>

	]]>
	</html_data>
</module>
