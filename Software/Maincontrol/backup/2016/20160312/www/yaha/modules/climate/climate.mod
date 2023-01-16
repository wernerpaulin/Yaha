<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>climate</id>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_temperature</icon>
	</info>
	<html_data>
	<![CDATA[
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_dashboard; visible: onload">
			<p>$yaha_tuid:cont0001$</p>
		  	<p>Living room temperature: <span id="ioActTempLivingroom" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>$deg$C show">tbd...</span></p>
		  	<p>Living room panel set point: <span id="ioSetTempLivingroom" yaha="io_mode:read_cyclic">tbd...</span></p>
			<p><input type="radio" name="uiSwitch1" id="switch1" value="radio1" yaha="io_mode:read_cyclic">Switch 1</p>
			
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
