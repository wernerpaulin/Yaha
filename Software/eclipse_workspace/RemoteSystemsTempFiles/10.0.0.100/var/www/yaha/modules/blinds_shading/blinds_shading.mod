<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>blinds_shading</id>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_blinds</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			function moduleInit()
			{

			}
		</script>
		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_dashboard; visible: onload">
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div data-role="collapsible" data-collapsed="false">
						<h4>Guest bathroom shutter</h4>
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestShutterUp" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_SHUTTER_UP">up</a>
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestShutterDown" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_SHUTTER_DOWN">down</a>
						<p>Switch: <span id="uiIoGuestBathroomSwitchedOn" yaha="io_mode:read_cyclic ; value_map:1=on,0=off">tbd...</span></p>
						<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGuestShutterTeach" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_SHUTTER_TEACH">learn</a>
						<p>Date and Time enable: <input type="checkbox" id="uiGuestBathTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></p>
	
					  	<!-- the following line stores the flags used to send button trigger to server -->
						<div style="visibility:hidden">
							<span id="uiGuestBathUp" yaha="tag_group:GUEST_SHUTTER_UP">1</span>
							<span id="uiGuestBathDown" yaha="tag_group:GUEST_SHUTTER_DOWN">1</span>
							<span id="uiGuestBathTeach" yaha="tag_group:GUEST_SHUTTER_TEACH">1</span>
						</div>
					</div>
				</div>
			</div>
		</div>
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0002$ ;module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0002$</p>
		</div>
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0003$ ;module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0003$</p>
		</div>
		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0004$ ;module_icon: yaha_floorplan">
			<p>$yaha_tuid:cont0004$</p>
		</div>
	]]>
	</html_data>
</module>
