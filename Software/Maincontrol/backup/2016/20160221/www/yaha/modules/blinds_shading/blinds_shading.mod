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
						<h4>Guest bathroom blinds</h4>
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_OPEN">open</a>
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_CLOSE">close</a>
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_STOP">stop</a>

						<p>
						Set position<input type="text" id="uiGuestBathBlindSetPosition" yaha="io_mode:read_cyclic, write_enter">
				    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_START_MOVEMENT">go</a>
						</p>

						<p>Date and Time enable: <input type="checkbox" id="uiGuestBathBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></p>
						<p>Anit-glare enable: <input type="checkbox" id="uiGuestBathBlindAntiGlareEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein"></input></p>

						<p>Opening: <span id="uiIoGuestBathBlindStatusOpening" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
						<p>Fully open: <span id="uiIoGuestBathBlindStatusFullyOpen" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
						<p>Closing: <span id="uiIoGuestBathBlindStatusClosing" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
						<p>Fully closed: <span id="uiIoGuestBathBlindStatusFullyClosed" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
						<p>Stopped: <span id="uiIoGuestBathBlindStatusStopped" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>

						<p>Calculated motor position: <span id="uiGuestBathBlindCalcMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
						<p>Actual motor position: <span id="uiIoGuestBathBlindStatusActMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>

						<p>Actual blind position: <span id="uiGuestBathBlindActPosition" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
						
						<a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGuestBathBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_TEACH">learn</a>

					  	<!-- the following line stores the flags used to send button trigger to server -->
						<div style="visibility:hidden">
							<span id="uiGuestBathBlindOpen" yaha="tag_group:GUEST_BATH_BLIND_OPEN">1</span>
							<span id="uiGuestBathBlindClose" yaha="tag_group:GUEST_BATH_BLIND_CLOSE">1</span>
							<span id="uiGuestBathBlindStop" yaha="tag_group:GUEST_BATH_BLIND_STOP">1</span>
							<span id="uiGuestBathBlindTeach" yaha="tag_group:GUEST_BATH_BLIND_TEACH">1</span>
							<span id="uiGuestBathBlindCmdStartMovePosition" yaha="tag_group:GUEST_BATH_BLIND_START_MOVEMENT">1</span>
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
