<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>lights_switches</id>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_bulb</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			function moduleInit()
			{

			}
		</script>

		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_dashboard; visible: onload">
			<table data-role="table" class="ui-responsive ui-shadow">
				<thead>
					<tr>
					    <th>Info / Action</th>
					    <th>Light 1</th>
					    <th>Light 2</th>
					    <th>Garage door</th>
					    <th>Garage light</th>
					</tr>
				</thead>
				<tbody>
					  <tr>
					    <td>On / Off:</td>
					    <td>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight1On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_ON">on</a>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight1Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_OFF">off</a>
					    </td>
					    <td>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight2On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_ON">on</a>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLight2Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_OFF">off</a>
					    </td>
					    <td>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageImpulse" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_IMPULSE">on</a>
					    </td>
					    <td>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageLightOn" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_ON">on</a>
					    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageLightOff" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_OFF">off</a>
					    </td>
					  </tr>
					  <tr>
					    <td>On time:</td>
					    <td><span id="uiIoLight1onTime" yaha="io_mode:read_cyclic">tbd...</span></td>
					    <td><span id="uiIoLight2onTime" yaha="io_mode:read_cyclic">tbd...</span></td>
					    <td></td>
					    <td><span id="uiIoGarageLightOnTime" yaha="io_mode:read_cyclic">tbd...</span></td>
					  </tr>
					  <tr>
					    <td>Energy:</td>
					    <td><span id="uiIoLight1energy" yaha="io_mode:read_cyclic">tbd...</span></td>
					    <td><span id="uiIoLight2energy" yaha="io_mode:read_cyclic">tbd...</span></td>
					    <td></td>
					    <td><span id="uiIoGarageLightEnergy" yaha="io_mode:read_cyclic">tbd...</span></td>
					  </tr>
					  <tr>
					    <td>Switched:</td>
					    <td><span id="uiIoLight1switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
					    <td><span id="uiIoLight2switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
					    <td><span id="uiIoGarageSwitchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
					    <td><span id="uiIoGarageLightSwitchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
					  </tr>
					  <tr>
					    <td>Learning:</td>
					    <td>
					    	<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLight1teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_TEACH">learn</a>
					    </td>
					    <td>
					    	<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLight2teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_TEACH">learn</a>
					    </td>
					    <td>
					    	<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGarageTeach" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_TEACH">learn</a>
					    </td>
					    <td>
					    	<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGarageLightTeach" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_LIGHT_TEACH">learn</a>
					    </td>
					  </tr>
					  
					  <tr>
					    <td>Blink enable:</td>
					    <td><input type="checkbox" id="uiLight1BlinkEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td><input type="checkbox" id="uiLight2BlinkEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td></td>
					    <td></td>
					  </tr>
					  <tr>
					    <td>Impulse enable:</td>
					    <td><input type="checkbox" id="uiLight1ImpulseEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td><input type="checkbox" id="uiLight2ImpulseEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td></td>
					    <td></td>
					  </tr>
					  <tr>
					    <td>Off delay enable:</td>
					    <td><input type="checkbox" id="uiLight1OffDelayEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td><input type="checkbox" id="uiLight2OffDelayEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td></td>
					    <td></td>
					  </tr>
					  <tr>
					    <td>Date and Time enable:</td>
					    <td><input type="checkbox" id="uiLight1TimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td><input type="checkbox" id="uiLight2TimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td><input type="checkbox" id="uiGarageTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></td>
					    <td></td>
					  </tr>

				</tbody>
			</table>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<div style="visibility:hidden">
				<span id="uiLight1on" yaha="tag_group:LIGHT1_ON">1</span>
				<span id="uiLight1off" yaha="tag_group:LIGHT1_OFF">1</span>
				<span id="uiLight1teach" yaha="tag_group:LIGHT1_TEACH">1</span>
	
				<span id="uiLight2on" yaha="tag_group:LIGHT2_ON">1</span>
				<span id="uiLight2off" yaha="tag_group:LIGHT2_OFF">1</span>
				<span id="uiLight2teach" yaha="tag_group:LIGHT2_TEACH">1</span>
	
				<span id="uiGarageImpulse" yaha="tag_group:GARAGE_IMPULSE">1</span>
				<span id="uiGarageTeach" yaha="tag_group:GARAGE_TEACH">1</span>
	
				<span id="uiGuestBathUp" yaha="tag_group:GUEST_SHUTTER_UP">1</span>
				<span id="uiGuestBathDown" yaha="tag_group:GUEST_SHUTTER_DOWN">1</span>
				<span id="uiGuestBathTeach" yaha="tag_group:GUEST_SHUTTER_TEACH">1</span>
	
				<span id="uiGarageLightOn" yaha="tag_group:GARAGE_LIGHT_ON">1</span>
				<span id="uiGarageLightOff" yaha="tag_group:GARAGE_LIGHT_OFF">1</span>
				<span id="uiGarageLightTeach" yaha="tag_group:GARAGE_LIGHT_TEACH">1</span>
			</div>	

		</div>
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0002$ ; module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0002$</p>
		</div>
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0003$ ; module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0003$</p>
		</div>
		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0004$ ; module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0004$</p>
		</div>
		<div id="yaha_submodule_5" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0005$ ; module_icon: yaha_garden">
			<p>$yaha_tuid:cont0005$</p>
		</div>
	]]>
	</html_data>
</module>
