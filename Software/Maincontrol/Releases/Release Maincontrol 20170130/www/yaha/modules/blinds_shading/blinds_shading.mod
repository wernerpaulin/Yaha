<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>blinds_shading</id>
		<name>$yaha_tuid:modulename$</name>
		<order>10</order>
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
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_window_blind.svg" type="image/svg+xml" id="blindAnimationGuestBath"></object>
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
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="guestBathBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationGuestBath ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="guestBathBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationGuestBath; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGuestBathStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
									</td>
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
						<h3>$yaha_tuid:kitcheneastblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_window_blind.svg" type="image/svg+xml" id="blindAnimationKitchenEast"></object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenEastBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_EAST_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenEastBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_EAST_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenEastBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_EAST_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="kitchenEastBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="kitchenEastBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="kitchenEastBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationKitchenEast ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="kitchenEastBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationKitchenEast; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenEastStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_EAST_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:kitchensouthblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_window_blind.svg" type="image/svg+xml" id="blindAnimationKitchenSouth"></object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenSouthBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_SOUTH_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenSouthBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_SOUTH_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenSouthBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_SOUTH_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="kitchenSouthBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="kitchenSouthBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="kitchenSouthBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationKitchenSouth ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="kitchenSouthBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationKitchenSouth; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdKitchenSouthStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_SOUTH_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:loungesouthleftblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_door_blind.svg" type="image/svg+xml" id="blindAnimationLoungeSouthLeft"></object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthLeftBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthLeftBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthLeftBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="loungeSouthLeftBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="loungeSouthLeftBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="loungeSouthLeftBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationLoungeSouthLeft ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:1600 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="loungeSouthLeftBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationLoungeSouthLeft; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:175 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthLeftStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:loungesouthrightblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_door_blind.svg" type="image/svg+xml" id="blindAnimationLoungeSouthRight"></object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthRightBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_RIGHT_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthRightBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_RIGHT_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthRightBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_RIGHT_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="loungeSouthRightBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="loungeSouthRightBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="loungeSouthRightBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationLoungeSouthRight ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:1600 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="loungeSouthRightBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationLoungeSouthRight; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:175 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeSouthRightStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:loungeterraceblinds$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_door_wide_blind.svg" type="image/svg+xml" id="blindAnimationLoungeTerrace"></object>
									</td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeTerraceBlindOpen" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_TERRACE_BLIND_OPEN">$yaha_tuid:open$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeTerraceBlindClose" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_TERRACE_BLIND_CLOSE">$yaha_tuid:close$</a></td>
									<td><a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeTerraceBlindStop" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_TERRACE_BLIND_STOP">$yaha_tuid:stop$</a></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:timecontrol$</td>
									<td><input type="checkbox" id="loungeTerraceBlindTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:autoshading$</td>
									<td><input type="checkbox" id="loungeTerraceBlindAutoShadingEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input></td>
								</tr>
								<tr>
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="loungeTerraceBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationLoungeTerrace ; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:1600 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" 
										max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="loungeTerraceBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change; anim_target_id:blindAnimationLoungeTerrace; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:3 ; anim_attr_val_max:175 ; anim_val_min:0 ; anim_val_max:100">							
									</td>
									<td>
										<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdLoungeTerraceStartMovement" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_TERRACE_BLIND_START_MOVEMENT">$yaha_tuid:start$</a>
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
									<td>$yaha_tuid:guestbathroomblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGuestBathBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:GUEST_BATH_BLIND_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:kitcheneastblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdKitchenEastBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_EAST_BLIND_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:kitchensouthblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdKitchenSouthBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:KITCHEN_SOUTH_BLIND_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:loungesouthleftblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLoungeSouthLeftBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_LEFT_BLIND_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:loungesouthrightblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLoungeSouthRightBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_SOUTH_RIGHT_BLIND_TEACH">$yaha_tuid:start$</a></td>
								</tr>
								<tr>
									<td>$yaha_tuid:loungeterraceblinds$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdLoungeTerraceBlindTeach" yaha="io_mode:write_click ; tag_group_wr_click:LOUNGE_TERRACE_BLIND_TEACH">$yaha_tuid:start$</a></td>
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
									<td rowspan="4">
										<object data="../yaha/core/svg/symbol_window_blind.svg" type="image/svg+xml" id="blindAnimationMasterBath"></object>
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
									<td colspan="2">$yaha_tuid:actualshade$:</td>
									<td>
										<span 
										id="masterBathBlindActPosition" 
										yaha="io_mode:read_cyclic ; format:00 ; unit:%>% show ; anim_target_id:blindAnimationMasterBath; anim_svg_item_id:actBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100">00</span>
									</td>
								</tr>
								<tr>
									<td colspan="3">
										<input 
										type="number" 
										data-type="range" 
										min="0" max="100" 
										step="1" 
										value="0" 
										data-highlight="true" 
										id="masterBathBlindSetPosition" 
										yaha="io_mode:read_cyclic, write_change ; anim_target_id:blindAnimationMasterBath; anim_svg_item_id:setBlindPos ; anim_attribute:height ; anim_attr_val_min:10 ; anim_attr_val_max:500 ; anim_val_min:0 ; anim_val_max:100"">
									</td>
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
			<span id="masterbathwindow_cmdStopID">cmdMasterBathBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="masterBathBlindOpen" yaha="tag_group:MASTER_BATH_BLIND_OPEN">1</span>
			<span id="masterBathBlindClose" yaha="tag_group:MASTER_BATH_BLIND_CLOSE">1</span>
			<span id="masterBathBlindStop" yaha="tag_group:MASTER_BATH_BLIND_STOP">1</span>
			<span id="masterBathBlindTeach" yaha="tag_group:MASTER_BATH_BLIND_TEACH">1</span>
			<span id="masterBathBlindCmdStartMovePosition" yaha="tag_group:MASTER_BATH_BLIND_START_MOVEMENT">1</span>

			<!-- kitchen east blinds -->
			<span id="kitcheneastwindow_headline">$yaha_tuid:kitcheneast_headline$</span>
			<span id="kitcheneastwindow_cmdOpenID">cmdKitchenEastBlindOpen</span>
			<span id="kitcheneastwindow_cmdCloseID">cmdKitchenEastBlindClose</span>
			<span id="kitcheneastwindow_cmdStopID">cmdKitchenEastBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="kitchenEastBlindOpen" yaha="tag_group:KITCHEN_EAST_BLIND_OPEN">1</span>
			<span id="kitchenEastBlindClose" yaha="tag_group:KITCHEN_EAST_BLIND_CLOSE">1</span>
			<span id="kitchenEastBlindStop" yaha="tag_group:KITCHEN_EAST_BLIND_STOP">1</span>
			<span id="kitchenEastBlindTeach" yaha="tag_group:KITCHEN_EAST_BLIND_TEACH">1</span>
			<span id="kitchenEastBlindCmdStartMovePosition" yaha="tag_group:KITCHEN_EAST_BLIND_START_MOVEMENT">1</span>

			<!-- kitchen south blinds -->
			<span id="kitchensouthwindow_headline">$yaha_tuid:kitchensouth_headline$</span>
			<span id="kitchensouthwindow_cmdOpenID">cmdKitchenSouthBlindOpen</span>
			<span id="kitchensouthwindow_cmdCloseID">cmdKitchenSouthBlindClose</span>
			<span id="kitchensouthwindow_cmdStopID">cmdKitchenSouthBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="kitchenSouthBlindOpen" yaha="tag_group:KITCHEN_SOUTH_BLIND_OPEN">1</span>
			<span id="kitchenSouthBlindClose" yaha="tag_group:KITCHEN_SOUTH_BLIND_CLOSE">1</span>
			<span id="kitchenSouthBlindStop" yaha="tag_group:KITCHEN_SOUTH_BLIND_STOP">1</span>
			<span id="kitchenSouthBlindTeach" yaha="tag_group:KITCHEN_SOUTH_BLIND_TEACH">1</span>
			<span id="kitchenSouthBlindCmdStartMovePosition" yaha="tag_group:KITCHEN_SOUTH_BLIND_START_MOVEMENT">1</span>

			<!-- lounge south left blinds -->
			<span id="loungesouthleft_headline">$yaha_tuid:loungesouthleft_headline$</span>
			<span id="loungesouthleft_cmdOpenID">cmdLoungeSouthLeftBlindOpen</span>
			<span id="loungesouthleft_cmdCloseID">cmdLoungeSouthLeftBlindClose</span>
			<span id="loungesouthleft_cmdStopID">cmdLoungeSouthLeftBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="loungeSouthLeftBlindOpen" yaha="tag_group:LOUNGE_SOUTH_LEFT_BLIND_OPEN">1</span>
			<span id="loungeSouthLeftBlindClose" yaha="tag_group:LOUNGE_SOUTH_LEFT_BLIND_CLOSE">1</span>
			<span id="loungeSouthLeftBlindStop" yaha="tag_group:LOUNGE_SOUTH_LEFT_BLIND_STOP">1</span>
			<span id="loungeSouthLeftBlindTeach" yaha="tag_group:LOUNGE_SOUTH_LEFT_BLIND_TEACH">1</span>
			<span id="loungeSouthLeftBlindCmdStartMovePosition" yaha="tag_group:LOUNGE_SOUTH_LEFT_BLIND_START_MOVEMENT">1</span>

			<!-- lounge south right blinds -->
			<span id="loungesouthright_headline">$yaha_tuid:loungesouthright_headline$</span>
			<span id="loungesouthright_cmdOpenID">cmdLoungeSouthRightBlindOpen</span>
			<span id="loungesouthright_cmdCloseID">cmdLoungeSouthRightBlindClose</span>
			<span id="loungesouthright_cmdStopID">cmdLoungeSouthRightBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="loungeSouthRightBlindOpen" yaha="tag_group:LOUNGE_SOUTH_RIGHT_BLIND_OPEN">1</span>
			<span id="loungeSouthRightBlindClose" yaha="tag_group:LOUNGE_SOUTH_RIGHT_BLIND_CLOSE">1</span>
			<span id="loungeSouthRightBlindStop" yaha="tag_group:LOUNGE_SOUTH_RIGHT_BLIND_STOP">1</span>
			<span id="loungeSouthRightBlindTeach" yaha="tag_group:LOUNGE_SOUTH_RIGHT_BLIND_TEACH">1</span>
			<span id="loungeSouthRightBlindCmdStartMovePosition" yaha="tag_group:LOUNGE_SOUTH_RIGHT_BLIND_START_MOVEMENT">1</span>

			<!-- lounge terrace blinds -->
			<span id="loungeterrace_headline">$yaha_tuid:loungeterrace_headline$</span>
			<span id="loungeterrace_cmdOpenID">cmdLoungeTerraceBlindOpen</span>
			<span id="loungeterrace_cmdCloseID">cmdLoungeTerraceBlindClose</span>
			<span id="loungeterrace_cmdStopID">cmdLoungeTerraceBlindStop</span>
		  	<!-- the following line stores the flags used to send button trigger to server -->
			<span id="loungeTerraceBlindOpen" yaha="tag_group:LOUNGE_TERRACE_BLIND_OPEN">1</span>
			<span id="loungeTerraceBlindClose" yaha="tag_group:LOUNGE_TERRACE_BLIND_CLOSE">1</span>
			<span id="loungeTerraceBlindStop" yaha="tag_group:LOUNGE_TERRACE_BLIND_STOP">1</span>
			<span id="loungeTerraceBlindTeach" yaha="tag_group:LOUNGE_TERRACE_BLIND_TEACH">1</span>
			<span id="loungeTerraceBlindCmdStartMovePosition" yaha="tag_group:LOUNGE_TERRACE_BLIND_START_MOVEMENT">1</span>


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


	]]>
	</html_data>
</module>

