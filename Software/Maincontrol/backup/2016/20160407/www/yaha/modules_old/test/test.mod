<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>test</id>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_debug</icon>
	</info>
	<html_data>
	<![CDATA[
	<script type="text/javascript">
		function moduleInit()
		{
			yvInitSvgInteraction("groundfloor", function(objStr) { alert("clicked object:  " + objStr) })
		
			drawPieChart()
			drawLineChart()
			drawStackedAreaChart()
			drawLiveTrend()
		}
	</script>

	<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: Test 1 ; module_icon: yaha_multimedia; visible: onload">
		<p>Lights & switches</p>

		<div class="yaha_flex_container">
			<div class="yaha_flex_item">
				<h2>Clickable Floor Plan</h2>
				<object data="../yaha/core/svg/symbol_ground_floor.svg" type="image/svg+xml" id="groundfloor"></object>

				<h2>Flip switch</h2>
				<input type="checkbox" data-role="flipswitch" data-wrapper-class="yaha-flipswitch-onoff" data-off-text="Aus" data-on-text="Ein">

				<h2>Slider with number display</h2>
				<div style="text-align:center;">
					<span style="padding-left:55px; font-size: 30pt;" id="slider2">...</span>
					<input type="number" data-type="range" min="0" max="100" step="1" value="50" data-highlight="true" yaha="mirror_span_id: slider2">
				</div>

				<h2>Pop up dialog</h2>
				<a href="#yaha_popupOnOff" data-rel="popup" data-position-to="window" data-role="button" data-inline="true" data-transition="pop">Pop Up</a>
				<div data-role="popup" id="yaha_popupOnOff" class="ui-corner-all yaha-popup-container">
					<div class="yaha-popup-header">
						<h3>Wohnzimmer</h3>
					</div>
					<div class="yaha-popup-content">
						<a href="#" data-role="button" data-inline="true">Ein</a>    
						<a href="#" data-role="button" data-inline="true">Aus</a>  
						<a href="#" data-role="button" data-inline="true">Auto</a>  
					</div>
				</div>
			</div>

			<div class="yaha_flex_item">
				<h2>Table</h2>

				<table data-role="table" class="ui-responsive ui-shadow">
					<thead>
						<tr>
							<th>Device</th>
							<th>Power</th>
							<th>Chart</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>Fridge</td>
							<td>5 KWh</td>
							<td><a class="ui-nodisc-icon ui-btn ui-shadow ui-corner-all ui-icon-yaha_chart ui-btn-icon-notext" href="#"></a></td>
						</tr>
						<tr>
							<td>Washing machine</td>
							<td>12 KWh</td>
							<td><a class="ui-nodisc-icon ui-btn ui-shadow ui-corner-all ui-icon-yaha_chart ui-btn-icon-notext" href="#"></a></td>
						</tr>
						<tr>
							<td>Dryer</td>
							<td>20 KWh</td>
							<td><a class="ui-nodisc-icon ui-btn ui-shadow ui-corner-all ui-icon-yaha_chart ui-btn-icon-notext" href="#"></a></td>
						</tr>
						<tr>
							<td>Freezer</td>
							<td>8 KWh</td>
							<td><a class="ui-nodisc-icon ui-btn ui-shadow ui-corner-all ui-icon-yaha_chart ui-btn-icon-notext" href="#"></a></td>
						</tr>
					</tbody>
				</table>
			</div>

			<div class="yaha_flex_item">
				<h2>Pie chart</h2>
				<div id="pie_chart"></div>
			</div>

			<div class="yaha_flex_item">

			</div>
			
			<div class="yaha_flex_item">
				<h2>Collabsible content</h2>
				<div data-role="collapsible">
					<h4>On / off</h4>
					<p>Any content or widget</p>
				</div>
			</div>
		</div>


		<h2>Line chart</h2>
		<div id="line_chart"></div>

		<h2>Stacked area chart</h2>
		<div id="area_chart"></div>

		<h2>Live trend chart</h2>
		<div id="trend_chart"></div>
						

						
	</div>
	<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: Test 2 ;module_icon: yaha_debug">
		<p>Test - Sub module 1.2</p>
		<div class="yaha_flex_header">
			<p>Module header</p>

		</div>

		<div class="yaha_flex_container">
			<div class="yaha_flex_item">Flex 1 <br> Flex 1.2
			<div data-role="collapsible">
				<h4>Test</h4>
			</div>
			
			</div>
			<div class="yaha_flex_item">Flex 2</div>
			<div class="yaha_flex_item">Flex 3</div>
			<div class="yaha_flex_item">Flex 3</div>
			<div class="yaha_flex_item">Flex 3</div>
		</div>

		<div class="yaha_flex_footer">
			<p>Module footer</p>
		</div>		
	</div>
	<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: Test 3 ;module_icon: yaha_multimedia">
		<p>Test - Sub module 1.3</p>
	</div>
	<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: Test 4 ;module_icon: yaha_floorplan">
		<p>Test - Sub module 1.4</p>
	</div>
	<div id="yaha_submodule_5" class="yaha-submodule" yaha="module_name: Test 5 ;module_icon: yaha_multimedia">
		<p>Test - Sub module 1.5</p>
	</div>
	]]>
	</html_data>
</module>

