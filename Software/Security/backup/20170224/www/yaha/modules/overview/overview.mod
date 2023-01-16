<?xml version="1.0" encoding="UTF-8"?>
<module>
	<info>
		<id>overview</id>
		<name>$yaha_tuid:heating$</name>
		<order>0</order>
		<icon>yaha_heating</icon>
	</info>
	<html_data>
	<![CDATA[
		<script type="text/javascript">
			LOG_PATH             = "yaha/logs/"
			LOG_FILE_NAME_SUFFIX = ".csv"
			TREND_FILE_NAME_TRUNK  = "heating"
			STATISTICS_FILE_NAME_TRUNK  = "statistics_"
				
			var COLOR_YAHA_BLUE = "#0C4FFF"
			var ChartLegendTranslation = {}
			
				
			function onClickLanguageSelector(jqElement)
			{
				yvSwitchLanguage(jqElement.attr('href').substr(1))
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

				/* get current date and time of local machine when ever the user opens this module */
				getTimeFromLocalMachine();

				/* Show main navigation when overview page */
				//$( "#panelMainNav" ).panel( "open" );
				
				//set up PDI monitor just a bit once everything is loaded to avoid funny interference with jQuery!?
				setTimeout(pdiMonitorInit, 100)
			}
			

			function getTimeFromLocalMachine()
			{
				/* get current date of local machine which runs the browser to initalize input fields for usability */
				setDate = new Date()	
				$("#setDateString").val(setDate.toISOString().substring(0, 10));
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
				$("#setTimeString").val( setHours + ":" + setMinutes)
			}
			

			//++++++++++++++++++++++++++++++++++++++ PDI MONITOR SCRIPTING /Begin ++++++++++++++++++++++++++++++++++++++
			var PdiMonitorRowIndex;	
			var PdiMonitorTagsInTable = {}

			function pdiMonitorInit()
			{
				PdiMonitorRowIndex = 2;		//index of second row in table which is the first data row after the header row
				PdiMonitorTagsInTable = {}	//tag:input-ID

				//rebuild last table configuration
				cookieTagList = monitorReadTagListFromCookie()
				for (tag in cookieTagList)
				{	
					//add all valid tags into table
					if (cookieTagList[tag] != "")
					{
						addPdiMonitorRowToTable()
						lastRowIndex = PdiMonitorRowIndex - 1
						$("#" + "tag_name" + lastRowIndex).val(cookieTagList[tag])
					}
				}

				//hook call back function in juice frame work to get monitor data once processed by the juice frame work
				yjAddPostUpdateUiFunctionMonitorLiveData(monitorUiUpdate)

				//when table has been build up rebuild monitor table
				rebuildPdiMonitorTagsInTable()
			}

			//add new tag in table
			$("#pdi_mon_add_tag").on('click',function(){
				addPdiMonitorRowToTable()
			});

			//delete tag from table
			$("#pdi_mon_delete_tag").on('click', function() {
				$('.pdi_mon_tag_row:checkbox:checked').parents("tr").remove();
			    $('.pdi_mon_check_all').prop("checked", false); 
				check();
	
				//when table has been modified rebuild monitor table
				rebuildPdiMonitorTagsInTable()
			});
			
			//add one row to the table
			function addPdiMonitorRowToTable()
			{
				//prepare html code for table row
				var cell_html_string_checkbox  = "<td><input type='checkbox' class='pdi_mon_tag_row'/></td>"
				var cell_html_string_tag_name  = "<td><input type='text' id='tag_name"  + PdiMonitorRowIndex + "' name='tag_name[]'/></td>"
				var cell_html_string_tag_value = "<td><input type='text' id='tag_value" + PdiMonitorRowIndex + "' name='tag_value[]'/></td>"

			    var row_html_string= "";
			    row_html_string += "<tr>";
			    row_html_string += cell_html_string_checkbox
			    row_html_string += cell_html_string_tag_name
			    row_html_string += cell_html_string_tag_value
			    row_html_string +="</tr>";
				
				//add row to table
				$('#pdi_monitor').append(row_html_string);
				
				//add event listener for tag name which should be monitored
				$("#tag_name" + PdiMonitorRowIndex).on('change', function() {
					//PdiMonitorTagsInTable[$(this).val()] = this.id			//tag name = id of input field
					//console.log(PdiMonitorTagsInTable)

					//when table has been modified rebuild monitor table
					rebuildPdiMonitorTagsInTable()
				});				
				
				//add event listener for tag value which should be writte on change
				$("#tag_value" + PdiMonitorRowIndex).on('change', function() {
					tagValue = $(this).val() //current value of PDI tag to write

					//find input field in second column of row with PDI tag name corresponding to the value in third columns 
					//this = input-ID showing tag value -> parent() is its cell: <td> element -> parent() is its row: <tr> element 
					rowObj = $(this).parent().parent()
					//once we have the row -> access input field cell of second column and read current PDI tag name 
					tagName = rowObj.children("td:nth-child(2)").children('input').val() 

					yjAddMonitorTagToWriteCgiData(tagName, tagValue)					//hand over name and value of tag to juice frame work to write to server
				});				
				
				PdiMonitorRowIndex++;
			}
			

			//rebuild tag dictionary from current table entries
			function rebuildPdiMonitorTagsInTable()
			{
				PdiMonitorTagsInTable = {} 

				//go through second column of table and access input field
				$("#pdi_monitor").children("tbody").children("tr").children("td:nth-child(2)").children('input').each(function () {
					PdiMonitorTagsInTable[$(this).val()] = this.id			//tag name = id of input field
					//console.log(PdiMonitorTagsInTable)
				});

				//rebuild also cyclic read list for juice framework
				updateCyclicReadList()
				
				//keep current configuration as cookie in mind
				monitorWriteCookie(PdiMonitorTagsInTable)
			}

			
			//go through all currently tags entered in table and create a read list 
			function updateCyclicReadList()
			{
				var readCyclicMonitorTagIDs = new Array()

				//key of dictionary is tag name
				for (tag in PdiMonitorTagsInTable)
				{
					readCyclicMonitorTagIDs.push(tag)
				}
				
				//send list to juice framework
				yjDefineMonitorCyclicReadTagList(readCyclicMonitorTagIDs)
			}

			//update monitor table with live values
			function monitorUiUpdate(monitorLiveData)
			{
				for (tag in monitorLiveData)
				{
					//find third column of row to display value of tag
					//PdiMonitorTagsInTable[tag] = input-ID of this tag -> parent() is its cell: <td> element -> parent() is its row: <tr> element 
					rowObj = $('#' + PdiMonitorTagsInTable[tag]).parent().parent()
					
					//once we have the row -> access input field cell of third column and write current live value
					rowObj.children("td:nth-child(3)").children('input').each(function () 
																				{
																					//skip refresh of user interface if element has focus (user is editing)
																					if (this.id != document.activeElement.id)
																					{
																						$(this).val(monitorLiveData[tag])
																					}
																				});		
					
				}
			}


			function monitorWriteCookie(tagsInTable)
			{
				var tagListString = ""

				//key of dictionary is tag name
				for (tag in tagsInTable)
				{
					tagListString = tagListString.concat(tag)
					tagListString = tagListString.concat(",")
				}
								
				Cookies.set('COOKIE_YAHA_PDI_MONITOR', tagListString, { expires: 365 });  
			}
			
			
			function monitorReadTagListFromCookie()
			{
				tagList = []
				
				/* read cookies */
				tagListString = Cookies.get('COOKIE_YAHA_PDI_MONITOR')

				try 
				{
					if (tagListString.length > 0)
					{
						tagList = tagListString.split(",");
					}	
				}
				catch(err) 
				{
					tagList = []
				}					
				
				return tagList
			}


			
			function pdi_mon_select_all_tags() {
				$('input[class=pdi_mon_tag_row]:checkbox').each(function(){ 
					if($('input[class=pdi_mon_check_all]:checkbox:checked').length == 0){ 
						$(this).prop("checked", false); 
					} else {
						$(this).prop("checked", true); 
					} 
				});
			}
			
			function check(){
				obj=$('#pdi_monitor tr').find('input');
				$.each( obj, function( key, value ) {
				id=value.id;
				$('#'+id).html(key+1);
				});
				}


			//++++++++++++++++++++++++++++++++++++++ PDI MONITOR SCRIPTING /End ++++++++++++++++++++++++++++++++++++++

			
		</script>

	  	<!-- the following line stores the flags used to send button trigger to server -->
		<div style="visibility:hidden">

		</div>	


		
		<div id="yaha_submodule_1" class="yaha-submodule" yaha="module_name: $yaha_tuid:dashboard$ ; module_icon: yaha_dashboard; visible: onload">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:dashboard$</h1>
			</div>
			
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>TO BE DEFINED...</h3>

					</div>
				</div>
			</div>

		</div>
		

		<div id="yaha_submodule_2" class="yaha-submodule" yaha="module_name: $yaha_tuid:generalsettings$ ;module_icon: yaha_settings">
			<div class="yaha_flex_header">
				<h1 style="text-align:center">$yaha_tuid:settings$</h1>
			</div>
	
			<div class="yaha_flex_container">
				<div class="yaha_flex_item">
					<div id="languageSelector" class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:languageselection$</h3>
					</div>	
				</div>
				
				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
						<h3>$yaha_tuid:dateandtime$</h3>
						
						<table>
							<thead>
								<tr>
									<th></th>
									<th>$yaha_tuid:ondevice$</th>
									<th style="text-align:left; padding-left:10px">$yaha_tuid:new$</th>
								</tr>
							</thead>
							<tbody>						
					  			<tr>
			    					<td>$yaha_tuid:time$</td>
			    					<td style="padding-left: 15px"><span id="currentHour" yaha="io_mode:read_cyclic ; format:00"></span>:<span id="currentMinute" yaha="io_mode:read_cyclic ; format:00"></span>:<span id="currentSecond" yaha="io_mode:read_cyclic ; format:00"></span></td>
			    					<td style="padding-left: 10px"><input type="time" id="setTimeString" yaha="tag_group:DATETIME_SET" value=""></td>
			  					</tr>			
					  			<tr>
			    					<td>$yaha_tuid:date$</td>
			    					<td style="padding-left: 15px"><span id="currentDay" yaha="io_mode:read_cyclic ; format:00"></span>.<span id="currentMonth" yaha="io_mode:read_cyclic ; format:00"></span>.<span id="currentYear" yaha="io_mode:read_cyclic ; format:00"></span></td>
			    					<td style="padding-left: 10px"><input type="date" id="setDateString" yaha="tag_group:DATETIME_SET" value=""></td>
			  					</tr>	
			  					<tr>
			    					<td></td>
			    					<td></td>
			    					<td>
									  	<a href="#" data-role="button" data-icon="check" data-mini="true" data-inline="true" id="uicmdSetDateTime" yaha="io_mode:write_click ; tag_group_wr_click:DATETIME_SET">$yaha_tuid:apply$</a>
			    						<span style="visibility:hidden" id="cmdSetDateTime" yaha="tag_group:DATETIME_SET">1</span>
			    					</td>
			  					</tr>	
							</tbody>
						</table>					
					</div>	
					
				</div>


				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
					  	<table>
					  		<tbody>
					  			<tr>
					  				<td>$yaha_tuid:cycletime$</td>
					  				<td><span id="systemTickRunTime" yaha="io_mode:read_cyclic ; format:00.## ; unit:s>ms show">tbd...</span></td>
					  			</tr>
					  			<tr>
					  				<td>$yaha_tuid:cpuload$</td>
					  				<td><span id="cpuLoad" yaha="io_mode:read_cyclic ; format:00.# ; unit:N>% show">tbd...</span></td>
					  			</tr>
					  			<tr>
									<td colspan="2">
									  	<a href="#" data-role="button" data-mini="true" data-inline="true" id="stopSystem" yaha="io_mode:write_click ; tag_group_wr_click:STOP_SYSTEM">Stop Yaha System</a>
										<span style="visibility:hidden" id="cmdStopSystem" yaha="tag_group:STOP_SYSTEM">1</span>
									</td>
					  			</tr>
					  		</tbody>
					  	</table>
					</div>
				</div>

				<div class="yaha_flex_item">
					<div class="ui-body ui-body-a ui-corner-all ui-dashboard-panel">
				  		<h2 style="text-align:left">PDI Monitor</h2>
				  	
						<table id="pdi_monitor" cellspacing="0" width="40%" border=1>
						  <tr>
						    <th><input class='pdi_mon_check_all' type='checkbox' onclick="pdi_mon_select_all_tags()"/></th>
						    <th>Tag Name</th>
						    <th>Tag Value</th>
						  </tr>
						</table>
					</div>
				  	<div>
						<a href="#" data-role="button" data-icon="minus" data-mini="true" data-inline="true" id="pdi_mon_delete_tag">Delete</a>
						<a href="#" data-role="button" data-icon="plus" data-mini="true" data-inline="true" id="pdi_mon_add_tag">Add</a>
					</div>					
				</div>					




			</div>
	
			<div class="yaha_flex_footer">
			</div>		
						
		</div>
	]]>
	</html_data>
</module>

