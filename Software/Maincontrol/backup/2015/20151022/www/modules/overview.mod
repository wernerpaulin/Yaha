<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_bulb</icon>
	</info>
	<html_data>
	<![CDATA[
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_multimedia; visible: onload">
			<p>$yaha_tuid:cont0001$</p>
			<p>Count 1<input type="text" id="uiCount1" yaha="io_mode:read_cyclic, write_enter"></p>
					
		</div>
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0002$ ;module_icon: yaha_bulb">
			<p>$yaha_tuid:cont0002$</p>
		  	<p>Cycle time: <span id="uiSystemTickRunTime" yaha="io_mode:read_cyclic ; format:00.## ; unit:s>ms show">tbd...</span></p>
			<p>CPU load: <span id="uiCpuLoad" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>% show">tbd...</span></p>
		</div>
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0003$ ;module_icon: yaha_multimedia">
			<p>$yaha_tuid:cont0003$</p>
		  	<p>Living room temperature: <span id="uiIoActTempLivingroom" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>$deg$C show">tbd...</span></p>
		  	<p>Living room panel set point: <span id="uiIoSetTempLivingroom" yaha="io_mode:read_cyclic">tbd...</span></p>
		</div>
		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0004$ ;module_icon: yaha_bulb">
			<p>$yaha_tuid:cont0004$</p>
		</div>
		<div id="yaha_submodule_5" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0005$ ;module_icon: yaha_multimedia">
			<p>$yaha_tuid:cont0005$</p>
		</div>
	]]>
	</html_data>
</module>

