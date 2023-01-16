<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>overview</id>
		<name>$yaha_tuid:info0001$</name>
		<icon>yaha_home</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			var cgiData = {}
			var INDEX_DAY = 0
			var INDEX_MONTH = 1
			var INDEX_YEAR = 2
			var INDEX_HOUR = 3
			var INDEX_MINUTE = 4
			var INDEX_SECOND = 5
				
			function onClickLanguageSelector(jqElement)
			{
				yvSwitchLanguage(jqElement.attr('href').substr(1))
				$( "#languageSelector" ).collapsible( "collapse" );
			}
	
			function moduleInit()
			{
				//clear current languages 
				$("#languageSelector a").remove()
			
				//create new buttons according to list
				var mainNavHtmlString = ""
				for (languageID in AvailableLanguages)
				{
					mainNavHtmlString += '<a href="#' + languageID + '" class="ui-btn ui-corner-all ui-icon-yaha_flag_' + languageID + ' ui-nodisc-icon ui-btn-icon-left" style="text-align: left" onclick="onClickLanguageSelector($(this))">' + AvailableLanguages[languageID] + '</a>'
				}
				
				$(mainNavHtmlString).appendTo('#languageSelector');
				
				/* get current date of runtime system */
				cgiData["requestType"] = "getDateTime";
				
				jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
							function(dateString,status)
						    {	
						    	dateField = []
						    	dateField = dateString.split('.')
								$('#dayCurrent').html(dateField[INDEX_DAY])
								$('#monthCurrent').html(dateField[INDEX_MONTH])
								$('#yearCurrent').html(dateField[INDEX_YEAR])
								$('#hourCurrent').html(dateField[INDEX_HOUR])
								$('#minuteCurrent').html(dateField[INDEX_MINUTE])
								$('#secondCurrent').html(dateField[INDEX_SECOND])
						    });	
				
				/* get current date of local machine which runs the browser to initalize input fields for usability */
				setDate = new Date()	    
				$("#setDate").val(setDate.toISOString().substring(0, 10));
				setHours = ""
				setHours += setDate.getHours()
				if (setHours.length == 1)
				{
					setHours = "0" + setHours;		//add leading zero otherwise input field will not accept it: 09:00
				}
				
				setMinutes = ""
				setMinutes += setDate.getMinutes()
				if (setMinutes.length == 1)
				{
					setMinutes = "0" + setMinutes;		//add leading zero otherwise input field will not accept it: 09:00
				}

				/* apply time to input field */
				$("#setTime").val( setHours + ":" + setMinutes)

				/* one submodule shows the main navigation order which can be configured by the user */
			    $( "#moduleListOrderCfg" ).sortable();
			    $( "#moduleListOrderCfg" ).disableSelection();
			    <!-- Refresh list to the end of sort to have a correct display -->
			    $( "#moduleListOrderCfg" ).on( "sortstop", function(event, ui) 
					{
						$( "#moduleListOrderCfg" ).listview('refresh');
						  
						/* rebuild module view order after user changed order by drag & drop */
						ModuleViewOrder = [];
						//go through each list item and rebuild order list
						$("#moduleListOrderCfg" + " > li").each(function (index) 
							{
								//each list item looks like this: <li moduleNameID="overview">My Home</li>
								//update order list with ID of modules
								ModuleViewOrder.push($(this).attr("moduleNameID"))
							});
						
						//save list as cookie		
						yvWriteCookieModuleViewOrder(ModuleViewOrder)
					
						//update main navigation
						yvUpdateMainNavigation()
					});
				


				/* add current module order to sortable list so the user can change the order to the module appearance in the main navigation */
				for (i = 0; i < ModuleViewOrder.length; i++)
				{
					moduleNameID = ModuleViewOrder[i]
					moduleName = ModuleNameList[moduleNameID][MODULE_NAME_INDEX]
					//store moduleNameID as attribute in order to rebuild later the order list based on moduleNameID 
					$("#moduleListOrderCfg").append('<li moduleNameID="' + moduleNameID + '"' + '>' + moduleName + '</li>')
				}
					
			}
			
			
	        
			/* write new date and time to server */
			function setDateTime()
			{
				var cgiData = {}
				cgiData["requestType"] = "setDateTime";
				cgiData["setTime"] = $("#setTime").val();
				cgiData["setDate"] = $("#setDate").val();

				jQuery.post(CGI_SCRIPT_NAME_YAHA_VIEW, cgiData,
							function(dateString,status)
						    {	
						    	/* update current date and time with newly set values to indicate update */
						    	dateField = []
						    	dateField = dateString.split('.')
								$('#dayCurrent').html(dateField[INDEX_DAY])
								$('#monthCurrent').html(dateField[INDEX_MONTH])
								$('#yearCurrent').html(dateField[INDEX_YEAR])
								$('#hourCurrent').html(dateField[INDEX_HOUR])
								$('#minuteCurrent').html(dateField[INDEX_MINUTE])
								$('#secondCurrent').html(dateField[INDEX_SECOND])
						    });	
			}


		</script>
		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0001$ ; module_icon: yaha_dashboard">
			<p>$yaha_tuid:cont0001$</p>
			<p>Count 1<input type="text" id="uiCount1" yaha="io_mode:read_cyclic, write_enter" class="count_field"></p>
	
			<span class="yaha-symbol yaha-symbol-logo" style="width: 200px; line-height: 100px;"></span>
		</div>
		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0002$ ;module_icon: yaha_notificationcenter">
			<p>$yaha_tuid:cont0002$</p>
		</div>
		<div id="yaha_submodule_3" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0003$ ;module_icon: yaha_scenes">
			<p>$yaha_tuid:cont0003$</p>
		</div>
		<div id="yaha_submodule_4" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0004$ ;module_icon: yaha_debug">
			<p>$yaha_tuid:cont0004$</p>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
				  	Cycle time: <span id="uiSystemTickRunTime" yaha="io_mode:read_cyclic ; format:00.## ; unit:s>ms show">tbd...</span>
				  	<br>
					CPU load: <span id="uiCpuLoad" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>% show">tbd...</span>
				</div>
				<div class="yaha_flex_item">
					<textarea name="txtLogOutput" id="uiLogEnocean" rows="1" cols="1" style="width:640px;height:240px">
						deaktiviert wegen UDP-Frame size
				    </textarea>	
				</div>
			</div>
		
		</div>
		<div id="yaha_submodule_5" class="yaha-submodule" yaha="module_name: $yaha_tuid:nav0005$ ;module_icon: yaha_settings; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">Yaha Einstellungen</h1>
			</div>
	
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div data-role="collapsible" id="languageSelector">
						<h4>$yaha_tuid:cont0005$</h4>
					</div>	
				</div>
				
				<div class="yaha_flex_item">
					<div data-role="collapsible">
						<h4>$yaha_tuid:cont0006$</h4>
						
						<table data-role="table" class="ui-responsive ui-shadow">
							<thead>
								<tr>
									<th></th>
									<th>$yaha_tuid:cont0009$</th>
									<th>$yaha_tuid:cont0010$</th>
								</tr>
							</thead>
							<tbody>						
					  			<tr>
			    					<td>$yaha_tuid:cont0007$</td>
			    					<td><span id="hourCurrent"></span>:<span id="minuteCurrent"></span>:<span id="secondCurrent"></span></td>
			    					<td><input type="time" id="setTime" value=""></td>
			  					</tr>			
					  			<tr>
			    					<td>$yaha_tuid:cont0008$</td>
			    					<td><span id="dayCurrent"></span>.<span id="monthCurrent"></span>.<span id="yearCurrent"></span></td>
			    					<td><input type="date" id="setDate" value=""></td>
			  					</tr>	
			  					<tr>
			    					<td colspan=3>
						  				<a href="#" data-role="button" data-icon="check" data-mini="true" data-inline="true" onclick="setDateTime()">$yaha_tuid:cont0011$</a>
			    					</td>
			  					</tr>	
							</tbody>
						</table>					
					</div>	
					
				</div>

				<div class="yaha_flex_item">
					<div data-role="collapsible">
						<h4>$yaha_tuid:cont0012$</h4>
	
						<p>Current recipe: <span id="uiCurrentRcpName" yaha="io_mode:read_cyclic">tbd...</span></p>
					
					  	<p>Choose your home configuration: 
					  	<select id="uiRcpNameSelector" yaha="io_mode:read_cyclic, write_blur ; select_data:uiRcpNameList; select_value:uiCurrentRcpName">
					  		<!-- Options filled dynamically -->
					  		<option value=""></option>
					  	</select>

					  	<a href="#" data-role="button" data-mini="true" data-inline="true" id="cmdLoadRcp" yaha="io_mode:write_click ; tag_group_wr_click:RCP_LOAD">Load</a>
					  	<a href="#" data-role="button" data-mini="true" data-inline="true" id="cmdSaveRcp" yaha="io_mode:write_click ; tag_group_wr_click:RCP_SAVE">Save</a>

					
					  	<!-- the following line stores the flags used to send button trigger to server -->
						<div style="visibility:hidden"><span id="uiCmdLoadRcp" yaha="tag_group:RCP_LOAD">1</span><span id="uiCmdSaveRcp" yaha="tag_group:RCP_SAVE">1</span></div>
					  	<span style="visibility:hidden" id="uiRcpNameList" yaha="io_mode:read_cyclic">tbd...</span>
					  	
					
					  	<p>New recipe: <input type="text" id="uiNewRcpName" yaha="tag_group:RCP_CREATE">
					  	<a href="#" data-role="button" data-mini="true" data-inline="true" id="cmdCreateRcp" yaha="io_mode:write_click ; tag_group_wr_click:RCP_CREATE">$yaha_tuid:cont0013$</a>

						
					  	<!-- the following line stores the flags used to send button trigger to server -->
						<div style="visibility:hidden"><span id="uiCmdCreateRcp" yaha="tag_group:RCP_CREATE">1</span></div>			
					</div>
				</div>


				<div class="yaha_flex_item">
					<div data-role="collapsible">
						<h4>$yaha_tuid:cont0014$</h4>
					        <ul data-role="listview" data-inset="true" id="moduleListOrderCfg">
								<!-- dynamically added with moduleInit() -->
					        </ul>
					</div>
				</div>

			

			</div>
			
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

