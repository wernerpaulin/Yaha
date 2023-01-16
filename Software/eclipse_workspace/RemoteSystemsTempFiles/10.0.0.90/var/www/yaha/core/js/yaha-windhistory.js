/* Yaha-linechart.js (c) 2016 Werner Paulin */
/*
Wind history based on D3
http://bl.ocks.org/mbostock/4583749
*/

function drawWindHistoryChart(targetID, fileName, dotColor, legendTranslation)
{
	//DEBUGGING
	/*
	var data = [
	            [0, 2.0],
	            [90, 5.0],
	            [180, 8.0],
	            [270, 4.0]
	           ];
	*/
	
	var WIND_DIR_INDEX = 0
	var WIND_SPEED_INDEX = 1
	d3.csv(fileName, function(error, csv_data) 
						{ //WEPA
							var data = []
							data = csv_data.map(function(d)
							   					{ 
						   							return [ +d["windDirection"], +d["windSpeed"] ]; 
						   						});
							//console.log(data)
							   
							var width = 600,
							    height = 600,
							    radius = Math.min(width, height) / 2 - 60;
					
							var maxValue = d3.max(data, function(d) { return d[WIND_SPEED_INDEX]} );
							
							var r = d3.scale.linear()
							    .domain([0, maxValue])
							    .range([0, radius]);
					
							var line = d3.svg.line.radial()
							    .radius(function(d) { return r(d[WIND_SPEED_INDEX]); })
							    .angle(function(d) { return d[WIND_DIR_INDEX]; });
					
							$("#" + targetID).empty()
					
							var svg = d3.select("#" + targetID).append("svg")		
							    .attr("width", width)
							    .attr("height", height)
							    .append("g")
							    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
					
							var gr = svg.append("g")
							    .attr("class", "r axis")
							    .selectAll("g")
							    .data(r.ticks(5).slice(1))
							    .enter().append("g");
					
							gr.append("circle")
							    .attr("r", r);
					
							gr.append("text")										//value legend
							    .attr("y", function(d) { return -r(d) - 4; })
							    .attr("transform", "rotate(15)")
							    .style("text-anchor", "middle")
							    .text(function(d) { return d; });
					
							var ga = svg.append("g")								//angle legend
							    .attr("class", "a axis")
							    .selectAll("g")
							    .data(d3.range(0, 360, 30))
							    .enter().append("g")
							    .attr("transform", function(d) { return "rotate(" + d + ")"; });
					
							ga.append("line")
							    .attr("x2", radius);
					
							ga.append("text")
						    .attr("x", radius + 6)
						    .attr("dy", ".35em")
						    .style("text-anchor", function(d) { return d < 270 && d > 90 ? "end" : null; })		//label position around circle
						    .attr("transform", function(d) { return d < 270 && d > 90 ? "rotate(180 " + (radius + 6) + ",0)" : null; }) //label orientation around circle east/west
						    .style("font-size","16px") 
						    .text(function(d) { 
						    					d = d + 90	//for some strange reasons the labeling is 90 degree shifted?!
						    					if (d == 360)
						    						return legendTranslation["north"]
							    				else if (d == 90)
						    						return legendTranslation["east"]
								    			else if (d == 180)
						    						return legendTranslation["south"]
								    			else if (d == 270)
						    						return legendTranslation["west"]
						    					else
						    						return "";
						    					
						    					//return d + "&deg;"; 
						    				  });

						    // draw dots
						    svg.selectAll(".dot")
						        .data(data)
						        .enter().append("circle")
						        .attr("class", "dot")
						        .attr("r", 2.0)
						        .style("fill", dotColor)	//generic: d3.scale.category10() 

						        //convert polar coordinates (r=d[WIND_SPEED_INDEX], alpha=d[WIND_DIR_INDEX]) into cartesian coordinates (x, y), cos/sin expect radiants
						        //for some strange reasons the positioning is 90 degree shifted?!
						        .attr("cx", function(d) { return r(d[WIND_SPEED_INDEX]) * Math.cos((d[WIND_DIR_INDEX]-90) / 180 * Math.PI); })
						        .attr("cy", function(d) { return r(d[WIND_SPEED_INDEX]) * Math.sin((d[WIND_DIR_INDEX]-90) / 180 * Math.PI); })							   
							   
							   
						}); // End Data callback function
 }


