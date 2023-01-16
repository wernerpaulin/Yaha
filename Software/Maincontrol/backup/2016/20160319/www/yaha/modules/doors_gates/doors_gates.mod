<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>doors_gates</id>
		<name>$yaha_tuid:doorsandgates$</name>
		<icon>yaha_garage</icon>
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
			<span id="garageImpulse" yaha="tag_group:GARAGE_IMPULSE">1</span>
			<span id="garageTeach" yaha="tag_group:GARAGE_TEACH">1</span>
		</div>	

		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:groundfloor$ ; module_icon: yaha_floorplan ; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:groundfloor$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:garagedoor$</h3>
						<table>
							<tbody>
								<tr>
									<td rowspan="6">
										<span class="yaha-symbol yaha-symbol-light-off" style="width: 150px; line-height: 100px;"></span>
									</td>
									<td colspan="2"  style="padding-bottom: 1em;">
								    	<a href="#" data-role="button" data-inline="true" data-mini="true" id="cmdGarageImpulse" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_IMPULSE">$yaha_tuid:openclose$</a>
									</td>
								</tr>
								<tr>
									<td>
										$yaha_tuid:timecontrol$
									</td>
									<td>
										<input type="checkbox" id="garageTimeEnable" yaha="io_mode:read_cyclic, write_change" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="$yaha_tuid:off$" data-on-text="$yaha_tuid:on$"></input>
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
									<td>$yaha_tuid:garagedoor$</td>
									<td><a href="#" data-inline="true" data-role="button" data-mini="true" id="cmdGarageTeach" yaha="io_mode:write_click ; tag_group_wr_click:GARAGE_TEACH">$yaha_tuid:start$</a></td>
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
