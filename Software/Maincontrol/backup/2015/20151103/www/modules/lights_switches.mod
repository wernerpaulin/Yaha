<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_bulb</icon>
	</info>
	<html_data>
	<![CDATA[
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_dashboard; visible: onload">
			<table border="0">
			  <tr>
			    <th>Info / Action</th>
			    <th>Light 1</th>
			    <th>Light 2</th>
			  </tr>
			  <tr>
			    <td>On / Off:</td>
			    <td><button type="button" id="cmdLight1On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_ON">on</button><button type="button" id="cmdLight1Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_OFF">off</button></td>
			    <td><button type="button" id="cmdLight2On" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_ON">on</button><button type="button" id="cmdLight2Off" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_OFF">off</button></td>
			  </tr>
			  <tr>
			    <td>On time:</td>
			    <td><span id="uiIoLight1onTime" yaha="io_mode:read_cyclic">tbd...</span></td>
			    <td><span id="uiIoLight2onTime" yaha="io_mode:read_cyclic">tbd...</span></td>
			  </tr>
			  <tr>
			    <td>Energy:</td>
			    <td><span id="uiIoLight1energy" yaha="io_mode:read_cyclic">tbd...</span></td>
			    <td><span id="uiIoLight2energy" yaha="io_mode:read_cyclic">tbd...</span></td>
			  </tr>
			  <tr>
			    <td>Switched:</td>
			    <td><span id="uiIoLight1switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
			    <td><span id="uiIoLight2switchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></td>
			  </tr>
			  <tr>
			    <td>Learning:</td>
			    <td><button type="button" id="cmdLight1teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT1_TEACH">learn</button></td>
			    <td><button type="button" id="cmdLight2teach" yaha="io_mode:write_click ; tag_group_wr_click:LIGHT2_TEACH">learn</button></td>
			  </tr>
		
			</table>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<div style="visibility:hidden">
			<span id="uiLight1on" yaha="tag_group:LIGHT1_ON">1</span>
			<span id="uiLight1off" yaha="tag_group:LIGHT1_OFF">1</span>
			<span id="uiLight2on" yaha="tag_group:LIGHT2_ON">1</span>
			<span id="uiLight2off" yaha="tag_group:LIGHT2_OFF">1</span>
			<span id="uiLight1teach" yaha="tag_group:LIGHT1_TEACH">1</span>
			<span id="uiLight2teach" yaha="tag_group:LIGHT2_TEACH">1</span>
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
	]]>
	</html_data>
</module>
