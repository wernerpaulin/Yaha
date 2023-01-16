<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>blinds_shading</id>
		<name>$yaha_tuid:modulename$</name>
		<icon>yaha_blinds</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			function moduleInit()
			{
				yvInitSvgInteraction("gf_overview", floorplan_click_handler)
				yvInitSvgInteraction("1f_overview", floorplan_click_handler)
			}
			
			function floorplan_click_handler(clickedObjID)
			{
				//console.log("object ID clicked: " + clickedObjID);
				//Remove legacy headline
				$("#blindHeadline").html("")
				//set headline of dialog: ID of span tag where text comes from must have a generic ID name: 
				//#blindHeadline 						...actual headline text
				//"#" + clickedObjID + "_headline"		...i.e.: guestbathwindow_headline: contains the headline for each window depending on language
				$("#blindHeadline").html($("#" + clickedObjID + "_headline").html())

				if ($("#blindHeadline").html() == "")
				{
					console.log("No pop-up defined for " + clickedObjID)
					return;
				}

				//set ID of hyperlink which should be sent a trigger event which is then initiating yaha write procedure
				//remove previous information to avoid legacy trigger
				$("#cmdOpenID").html("")
				$("#cmdCloseID").html("")
				$("#cmdStopID").html("")
				
				//#cmdOpenID							...ID of hyperlink of a certain window to which a click event will be sent
				//#"#" + clickedObjID + "_cmdOpenID"	...i.e.: guestbathwindow_cmdOpenID: contains the actual ID of the hyperlink which is monitored by Yaha
				$("#cmdOpenID").html($("#" + clickedObjID + "_cmdOpenID").html())
				$("#cmdCloseID").html($("#" + clickedObjID + "_cmdCloseID").html())
				$("#cmdStopID").html($("#" + clickedObjID + "_cmdStopID").html())

				//open dialog
				$( "#dialogBlindOpenClose" ).popup("open");
			}
			
			//will be called by the pop-up and sends a click event to an ID which is set by cmdOpenID
			function onClickBlindOpen()
			{
				$( "#" + $("#cmdOpenID").html() ).trigger("click")
				$( "#dialogBlindOpenClose" ).popup("close");
			}

			//will be called by the pop-up and sends a click event to an ID which is set by cmdCloseID
			function onClickBlindClose()
			{
				$( "#" + $("#cmdCloseID").html() ).trigger("click")
				$( "#dialogBlindOpenClose" ).popup("close");
			}

			//will be called by the pop-up and sends a click event to an ID which is set by cmdStopID
			function onClickBlindStop()
			{
				$( "#" + $("#cmdStopID").html() ).trigger("click")
				$( "#dialogBlindOpenClose" ).popup("close");
			}

		</script>

		<!-- TODO: add new shutters here -->
		<div style="visibility:hidden">
			<!-- standard ids which are used by the pop-up and which will have as text the corresponding real cmd-ID -->
			<span id="cmdOpenID"></span>
			<span id="cmdCloseID"></span>
			<span id="cmdStopID"></span>

			<!-- guest bathroom blinds -->
			<span id="guestbathwindow_headline">$yaha_tuid:guestbathwindow_headline$</span>
			<span id="guestbathwindow_cmdOpenID">cmdGuestBathBlindOpen</span>
			<span id="guestbathwindow_cmdCloseID">cmdGuestBathBlindClose</span>
			<span id="guestbathwindow_cmdStopID">cmdGuestBathBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="guestBathBlindOpen" yaha="tag_group:GUEST_BATH_BLIND_OPEN">1</span>
			<span id="guestBathBlindClose" yaha="tag_group:GUEST_BATH_BLIND_CLOSE">1</span>
			<span id="guestBathBlindStop" yaha="tag_group:GUEST_BATH_BLIND_STOP">1</span>
			<span id="guestBathBlindTeach" yaha="tag_group:GUEST_BATH_BLIND_TEACH">1</span>
			<span id="guestBathBlindCmdStartMovePosition" yaha="tag_group:GUEST_BATH_BLIND_START_MOVEMENT">1</span>

			<!-- master bathroom blinds -->
			<span id="masterbathwindow_headline">$yaha_tuid:masterbathwindow_headline$</span>
			<span id="masterbathwindow_cmdOpenID">cmdMasterBathBlindOpen</span>
			<span id="masterbathwindow_cmdCloseID">cmdMasterBathBlindClose</span>
			<span id="mastertbathwindow_cmdStopID">cmdMasterBathBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="masterBathBlindOpen" yaha="tag_group:MASTER_BATH_BLIND_OPEN">1</span>
			<span id="masterBathBlindClose" yaha="tag_group:MASTER_BATH_BLIND_CLOSE">1</span>
			<span id="masterBathBlindStop" yaha="tag_group:MASTER_BATH_BLIND_STOP">1</span>
			<span id="masterBathBlindTeach" yaha="tag_group:MASTER_BATH_BLIND_TEACH">1</span>
			<span id="masterBathBlindCmdStartMovePosition" yaha="tag_group:MASTER_BATH_BLIND_START_MOVEMENT">1</span>
		</div>

		<div data-role="popup" id="dialogBlindOpenClose" class="ui-corner-all yaha-popup-container">
			<div class="yaha-popup-header">
				<h3 id="blindHeadline"></h3>
			</div>
			<div class="yaha-popup-content">
				<a href="#" data-role="button" data-inline="true" onclick="onClickBlindOpen();">$yaha_tuid:open$</a>    
				<a href="#" data-role="button" data-inline="true" onclick="onClickBlindClose();">$yaha_tuid:close$</a>  
				<a href="#" data-role="button" data-inline="true" onclick="onClickBlindStop();">$yaha_tuid:stop$</a>  
			</div>
		</div>

		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:groundfloor$ ; module_icon: yaha_floorplan; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:groundfloor$</h1>
			</div>

			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:overview$</h3>
						<object data="../yaha/core/svg/floorplan_gf.svg" type="image/svg+xml" id="gf_overview"></object>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:guestbathroomblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="3">
										<object 
											data="../yaha/core/svg/symbol_window_blind.svg" type="image/svg+xml" 
											id="blindAnimationGuestBath" 
											yaha="anim_svg_item_ids:actBlindPos,setBlindPos ; anim_value_ids:guestBathBlindActPosition,guestBathBlindSetPosition ; anim_attributes:height,height ; anim_attr_val_min:12,12 ; anim_attr_val_max:500,500 ; anim_val_min:0,0 ; anim_val_max:100,100">
										</object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="guestBathBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="guestBathBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td style="padding-left:40px">$yaha_tuid:set$: <span id="guestBathBlindSetPositionTxt"></span> %</td>
									<td colspan="2">$yaha_tuid:act$: <span id="guestBathBlindActPosition" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></td>
									<td></td>
								</tr>
								<tr>
									<td colspan="3"><input type="number" data-type="range" min="0" max="100" step="1" value="0" data-highlight="true" id="guestBathBlindSetPosition" yaha="io_mode:read_cyclic, write_change; mirror_span_id: guestBathBlindSetPositionTxt"></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_START_MOVEMENT">$yaha_tuid:start$</a></td>
								</tr>
							</tbody>
						</table>
						
						<!-- DEBUGGING div style="visibility:hidden">
							<p>Opening: <span id="ioGuestBathBlindStatusOpening" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Fully open: <span id="ioGuestBathBlindStatusFullyOpen" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Closing: <span id="ioGuestBathBlindStatusClosing" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Fully closed: <span id="ioGuestBathBlindStatusFullyClosed" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Stopped: <span id="ioGuestBathBlindStatusStopped" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
	
							<p>Calculated motor position: <span id="guestBathBlindCalcMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
							<p>Actual motor position: <span id="ioGuestBathBlindStatusActMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
						</div-->
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:teaching$</h3>
						<table>
							<tbody>
								<tr>
									<td>$yaha_tuid:guestbathroomblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGuestBathBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_TEACH">$yaha_tuid:start$</a></td>
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
						<h3>$yaha_tuid:overview$</h3>
						<object data="../yaha/core/svg/floorplan_1f.svg" type="image/svg+xml" id="1f_overview"></object>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:masterbathroomblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="3">
										<span class="yaha-symbol yaha-symbol-window" style="width: 200px; line-height: 100px;"></span>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdMasterBathBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:MASTER_BATH_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdMasterBathBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:MASTER_BATH_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdMasterBathBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:MASTER_BATH_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="masterBathBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="masterBathBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td style="padding-left:50px">$yaha_tuid:set$: <span id="masterBathBlindSetPositionTxt"></span> %</td>
									<td colspan="2">$yaha_tuid:act$: <span id="masterBathBlindActPosition" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></td>
									<td></td>
								</tr>
								<tr>
									<td colspan="3"><input type="number" data-type="range" min="0" max="100" step="1" value="0" data-highlight="true" id="masterBathBlindSetPosition" yaha="io_mode:read_cyclic, write_change; mirror_span_id: masterBathBlindSetPositionTxt"></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdMasterBathStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:MASTER_BATH_BLIND_START_MOVEMENT">$yaha_tuid:start$</a></td>
								</tr>
							</tbody>
						</table>
						
						<!-- DEBUGGING div style="visibility:hidden">
							<p>Opening: <span id="ioMasterBathBlindStatusOpening" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Fully open: <span id="ioMasterBathBlindStatusFullyOpen" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Closing: <span id="ioMasterBathBlindStatusClosing" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Fully closed: <span id="ioMasterBathBlindStatusFullyClosed" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
							<p>Stopped: <span id="ioMasterBathBlindStatusStopped" yaha="io_mode:read_cyclic ; value_map:1=true,0=false">tbd...</span></p>
	
							<p>Calculated motor position: <span id="masterBathBlindCalcMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
							<p>Actual motor position: <span id="ioMasterBathBlindStatusActMotorPos" yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show">tbd...</span></p>
						</div-->
					</div>
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:teaching$</h3>
						<table>
							<tbody>
								<tr>
									<td>$yaha_tuid:masterbathroomblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdMasterBathBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:MASTER_BATH_BLIND_TEACH">learn</a></td>
								</tr>
							</tbody>
						</table>	
					</div>
				</div>
			</div>
		</div>

	]]>
	</html_data>
</module>

