<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>lights_switches</id>
		<name>$yaha_tuid:lightsandswitches$</name>
		<icon>yaha_bulb</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			function moduleInit()
			{

			}
		</script>

	  	<!-- the following line stores the flags used to send button trigger to server -->
		<div style="visibility:hidden">
			<span id="light1on" yaha="tag_group:LIGHT1_ON">1</span>
			<span id="light1off" yaha="tag_group:LIGHT1_OFF">1</span>
			<span id="light1teach" yaha="tag_group:LIGHT1_TEACH">1</span>

			<span id="light2on" yaha="tag_group:LIGHT2_ON">1</span>
			<span id="light2off" yaha="tag_group:LIGHT2_OFF">1</span>
			<span id="light2teach" yaha="tag_group:LIGHT2_TEACH">1</span>

			<span id="garageLightOn" yaha="tag_group:GARAGE_LIGHT_ON">1</span>
			<span id="garageLightOff" yaha="tag_group:GARAGE_LIGHT_OFF">1</span>
			<span id="garageLightTeach" yaha="tag_group:GARAGE_LIGHT_TEACH">1</span>
		</div>	

		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:groundfloor$ ; module_icon: yaha_floorplan ; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:groundfloor$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:garage$</h3>
						<table>
							<tbody>
								<tr>
									<td>
										<span class="yaha-symbol yaha-symbol-light-off" style="width: 150px; line-height: 100px;"></span>
									</td>
									<td colspan="2"  style="padding-bottom: 1em;">
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageLightOn" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_ON">$yaha_tuid:on$</a>
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageLightOff" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_OFF">$yaha_tuid:off$</a>
										<span id="ioGarageLightSwitchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:testswitch1$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="6">
										<span class="yaha-symbol yaha-symbol-light-off" style="width: 150px; line-height: 100px;"></span>
									</td>
									<td colspan="2"  style="padding-bottom: 1em;">
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight1On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_ON">$yaha_tuid:on$</a>
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight1Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_OFF">$yaha_tuid:off$</a>
										<span id="ioLight1switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:energy$
									</td>
									<td>
										<span id="ioLight1energy" yaha="io_mode:read_cyclic">tbd...</span>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:blinkmode$
									</td>
									<td>
										<input type="checkbox" id="light1BlinkEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:offdelay$
									</td>
									<td>
										<input type="checkbox" id="light1OffDelayEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:impulsemode$
									</td>
									<td>
										<input type="checkbox" id="light1ImpulseEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:timecontrol$
									</td>
									<td>
										<input type="checkbox" id="light1TimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:teaching$</h3>
						<table>
							<tbody>
								<tr>
									<td>$yaha_tuid:testswitch1$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLight1teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:garage$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGarageLightTeach" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_TEACH">$yaha_tuid:start$</a></td>
								</tr>
							</tbody>
						</table>	
					</div>
				</div>
			</div>



		</div>
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:firstfloor$ ; module_icon: yaha_floorplan">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:firstfloor$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:testswitch2$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="6">
										<span class="yaha-symbol yaha-symbol-light-off" style="width: 150px; line-height: 100px;"></span>
									</td>
									<td colspan="2"  style="padding-bottom: 1em;">
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight2On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_ON">$yaha_tuid:on$</a>
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight2Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_OFF">$yaha_tuid:off$</a>
										<span id="ioLight2switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:energy$
									</td>
									<td>
										<span id="ioLight2energy" yaha="io_mode:read_cyclic">tbd...</span>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:blinkmode$
									</td>
									<td>
										<input type="checkbox" id="light2BlinkEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:offdelay$
									</td>
									<td>
										<input type="checkbox" id="light2OffDelayEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:impulsemode$
									</td>
									<td>
										<input type="checkbox" id="light2ImpulseEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:timecontrol$
									</td>
									<td>
										<input type="checkbox" id="light2TimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:teaching$</h3>
						<table>
							<tbody>
								<tr>
									<td>$yaha_tuid:testswitch2$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLight2teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_TEACH">$yaha_tuid:start$</a></td>
								</tr>
							</tbody>
						</table>	
					</div>
				</div>


		</div>
	]]>
	</html_data>
</module>
