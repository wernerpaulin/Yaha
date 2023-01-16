/* Yaha-view | (c) 2015 Werner Paulin */
/* Yaha view automation */
/*
Chart control based on D3

ACHTUNG: Funktionen haben hartkodierte tag-IDs und Datenquellen-Referenzen!!! - NUR PROOF OF CONCEPT
*/


	function drawPieChart()
	{
		var width = 360,
		    height = 360,
		    radius = Math.min(width, height) / 2;

        var legendRectSize = 18;                                  // NEW
        var legendSpacing = 4;                                    // NEW
		
		var color = d3.scale.category20();			
		
		var arc = d3.svg.arc()
		    .outerRadius(radius - 10)
		    .innerRadius(radius - 60);
		
		var pie = d3.layout.pie()
		    .sort(null)
		    .value(function(d) { return d.population; });
		
		var svg = d3.select('#pie_chart')
			.append('svg')
		    .attr("width", width)
		    .attr("height", height)
		  .append("g")
		    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
		
		d3.csv("reports/piechart_data.csv", function(error, data) {
			if (error) throw error;
		  data.forEach(function(d) {
		    d.population = +d.population;					//POPULATION -> generisch
		  });
		
		  var g = svg.selectAll(".arc")
		      .data(pie(data))
		    .enter().append("g")
		      .attr("class", "arc");
		
		  g.append("path")
		      .attr("d", arc)
		      .style("fill", function(d) { return "#808080"; })		//start animation with a grey ring
			    .transition()
			    .duration(1000)

				  .attrTween('d', function(finish) {
				        var start = {
				                startAngle: 0,
				                endAngle: 0
				            };
				        var i = d3.interpolate(start, finish);
				        return function(d) { return arc(i(d)); };
				  })
		      .style("fill", function(d) { return color(d.data.age); }); //set correct colors for segments	AGE -> GENERISCH


		      
		  g.append("text")
		      .attr("transform", function(d) { return "translate(" + arc.centroid(d) + ")"; })
		      .attr("dy", ".35em")
		      .style("text-anchor", "middle")
		      .text(function(d) { return d.data.age; });

        var legend = svg.selectAll('.legend')                     // NEW
          .data(color.domain())                                   // NEW
          .enter()                                                // NEW
          .append('g')                                            // NEW
          .attr('class', 'legend')                                // NEW
          .attr('transform', function(d, i) {                     // NEW
            var height = legendRectSize + legendSpacing;          // NEW
            var offset =  height * color.domain().length / 2;     // NEW
            var horz = -2 * legendRectSize;                       // NEW
            var vert = i * height - offset;                       // NEW
            return 'translate(' + horz + ',' + vert + ')';        // NEW
          });                                                     // NEW

        legend.append('rect')                                     // NEW
          .attr('width', legendRectSize)                          // NEW
          .attr('height', legendRectSize)                         // NEW
          .style('fill', color)                                   // NEW
          .style('stroke', color);                                // NEW
          
        legend.append('text')                                     // NEW
          .attr('x', legendRectSize + legendSpacing)              // NEW
          .attr('y', legendRectSize - legendSpacing)              // NEW
          .text(function(d) { return d; });                       // NEW
		
		});	
	}


	function drawLineChart()
	{

		var margin = {top: 20, right: 80, bottom: 30, left: 50},
	    width = 960 - margin.left - margin.right,
	    height = 500 - margin.top - margin.bottom;

	var parseDate = d3.time.format("%d.%m.%Y %H:%M").parse;	//https://github.com/mbostock/d3/wiki/Time-Formatting

	var x = d3.time.scale()
	    .range([0, width]);

	var y = d3.scale.linear()
	    .range([height, 0]);

	var color = d3.scale.category10();

	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");

	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left");

	var line = d3.svg.line()
	    .interpolate("basis")
	    .x(function(d) { return x(d.date); })
	    .y(function(d) { return y(d.temperature); });

	var svg = d3.select('#line_chart')
		.append('svg')
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	d3.csv("reports/linechart_data.csv", function(error, data) {
		  if (error) throw error;

	  color.domain(d3.keys(data[0]).filter(function(key) { return key !== "date"; }));

	  data.forEach(function(d) {
	    d.date = parseDate(d.date);
	  });

	  var cities = color.domain().map(function(name) {
	    return {
	      name: name,
	      values: data.map(function(d) {
	        return {date: d.date, temperature: +d[name]};
	      })
	    };
	  });

	  x.domain(d3.extent(data, function(d) { return d.date; }));

	  y.domain([
	    d3.min(cities, function(c) { return d3.min(c.values, function(v) { return v.temperature; }); }),
	    d3.max(cities, function(c) { return d3.max(c.values, function(v) { return v.temperature; }); })
	  ]);

	  svg.append("g")
	      .attr("class", "x axis")
	      .attr("transform", "translate(0," + height + ")")
	      .call(xAxis);

	  svg.append("g")
	      .attr("class", "y axis")
	      .call(yAxis)
	    .append("text")
	      .attr("transform", "rotate(-90)")
	      .attr("y", 6)
	      .attr("dy", ".71em")
	      .style("text-anchor", "end")
	      .text("Temperature");

	  var city = svg.selectAll(".city")
	      .data(cities)
	    .enter().append("g")
	      .attr("class", "city");

	  city.append("path")
	      .attr("class", "line")
	      .attr("d", function(d) { return line(d.values); })
			.style("stroke", function(d) { return color(d.name); })

/* Animation - Begin */
  /* Add 'curtain' rectangle to hide entire graph */
  var curtain = svg.append('rect')
    .attr('x', -1 * width)
    .attr('y', -1 * height)
    .attr('height', height)
    .attr('width', width)
    .attr('class', 'curtain')
    .attr('transform', 'rotate(180)')
    .style('fill', '#ffffff')
    
  /* Create a shared transition for anything we're animating */
  var t = svg.transition()
    .delay(200)
    .duration(1000)
    .ease('linear')
    .each('end', function() {
      d3.select('line.guide')
        .transition()
        .style('opacity', 0)
        .remove()
    });

  t.select('rect.curtain')
    .attr('width', 0);
  t.select('line.guide')
    .attr('transform', 'translate(' + width + ', 0)')
/* Animation - End */

			
	  
	  	
	  var legend = svg.selectAll(".legend")
			      .data(color.domain().slice().reverse())
			    .enter().append("g")
			      .attr("class", "legend")
			      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });	  
	  
	  legend.append("rect")
	      .attr("x", width - 18)
	      .attr("width", 18)
	      .attr("height", 18)
	      .style("fill", color);

  legend.append("text")
	      .attr("x", width - 24)
	      .attr("y", 9)
	      .attr("dy", ".35em")
	      .style("text-anchor", "end")
	      .text(function(d) { return d; });	
	
	});		
		
		
		
	
	}


	function drawStackedAreaChart()
	{

		var format = d3.time.format("%m/%d/%y");
		
		var margin = {top: 20, right: 30, bottom: 30, left: 40},
		    width = 960 - margin.left - margin.right,
		    height = 500 - margin.top - margin.bottom;

		var x = d3.time.scale()
		    .range([0, width]);

		var y = d3.scale.linear()
		    .range([height, 0]);

		var z = d3.scale.category20();

		var xAxis = d3.svg.axis()
		    .scale(x)
		    .orient("bottom")
		    //.ticks() will be defined once the number of value
			.tickFormat(d3.time.format("%d.%m.%Y"));

		var yAxis = d3.svg.axis()
		    .scale(y)
		    .orient("left");

		var stack = d3.layout.stack()
		    .offset("zero")
		    .values(function(d) { return d.values; })
		    .x(function(d) { return d.date; })
		    .y(function(d) { return d.value; });

		var nest = d3.nest()
		    .key(function(d) { return d.key; });

		var area = d3.svg.area()
		    .interpolate("cardinal")
		    .x(function(d) { return x(d.date); })
		    .y0(function(d) { return y(d.y0); })
		    .y1(function(d) { return y(d.y0 + d.y); });

		var svg = d3.select('#area_chart')
			.append('svg')
		    .attr("width", width + margin.left + margin.right)
		    .attr("height", height + margin.top + margin.bottom)
		  .append("g")
		    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

		d3.csv("reports/barchart_data.csv", function(error, data) {
		  if (error) throw error;

		  data.forEach(function(d) {
		    d.date = format.parse(d.date);
		    d.value = +d.value;
		  });

		  var layers = stack(nest.entries(data));

		  xAxis.ticks(layers[0].values.length);
		  
		  x.domain(d3.extent(data, function(d) { return d.date; }));
		  y.domain([0, d3.max(data, function(d) { return d.y0 + d.y; })]);

		  svg.selectAll(".layer")
		      .data(layers)
		    .enter().append("path")
		      .attr("class", "layer")
		      .attr("d", function(d) { return area(d.values); })
		      .style("fill", function(d, i) { return z(i); });
		      
		  svg.append("g")
		      .attr("class", "x axis")
		      .attr("transform", "translate(0," + height + ")")
		      .call(xAxis);

		  svg.append("g")
		      .attr("class", "y axis")
		      .call(yAxis);

		  /* Animation - Begin */
		  /* Add 'curtain' rectangle to hide entire graph */
		  var curtain = svg.append('rect')
		    .attr('x', -1 * width)
		    .attr('y', -1 * height)
		    .attr('height', height)
		    .attr('width', width)
		    .attr('class', 'curtain')
		    .attr('transform', 'rotate(180)')
		    .style('fill', '#ffffff')
		    
		  /* Create a shared transition for anything we're animating */
		  var t = svg.transition()
		    .delay(200)
		    .duration(1000)
		    .ease('linear')
		    .each('end', function() {
		      d3.select('line.guide')
		        .transition()
		        .style('opacity', 0)
		        .remove()
		    });

		  t.select('rect.curtain')
		    .attr('width', 0);
		  t.select('line.guide')
		    .attr('transform', 'translate(' + width + ', 0)')
		/* Animation - End */
		  
		  
		  var legend = svg.selectAll(".legend")
	      .data(z.domain().slice().reverse())
	    .enter().append("g")
	      .attr("class", "legend")
	      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
	
		  legend.append("rect")
		      .attr("x", width - 18)
		      .attr("width", 18)
		      .attr("height", 18)
		      .style("fill", z);
		
		  legend.append("text")
		      .attr("x", width - 24)
		      .attr("y", 9)
		      .attr("dy", ".35em")
		      .style("text-anchor", "end")
		      .text(function(d) { return layers[d].key; });		  
		
		});		
		

	}	

	function drawLiveTrend()
	{
		 var t = -1;
		    var n = 40;
		    var duration = 750;

			var data1 = initialise(); 
			var data2 = initialise();  
			var data3 = initialise();  
			var data4 = initialise();  
					
			function initialise()
			{
				var time = -1;
				var arr = [];
				for (var i = 0; i < n; i++)
				{
					var obj = {
						time: ++time,
						value: Math.floor(Math.random()*100)
					};
					arr.push(obj);
				}	
				t = time;
				return arr;
			}
			
			// push a new element on to the given array
			function updateData(a)
			{
				var obj = {
					time:  t,  
					value: Math.floor(Math.random()*100)
				};
				a.push(obj);
			}
			
		    var margin = {top: 10, right: 10, bottom: 20, left: 40},
		        width = 960 - margin.left - margin.right,
		        height = 500 - margin.top - margin.bottom;
			 
		    var x = d3.scale.linear()
		        .domain([t-n+1, t])
		        .range([0, width]);
			 
		    var y = d3.scale.linear()
		        .domain([0, 100])
		        .range([height, 0]);
			 
		    var line = d3.svg.line()
				.interpolate("basis")
		        .x(function(d, i) { return x(d.time); })
		        .y(function(d, i) { return y(d.value); });
				
			var svg = d3.select('#trend_chart')
				.append('svg')
		        .attr("width", width + margin.left + margin.right)
		        .attr("height", height + margin.top + margin.bottom);

		    var g = svg.append("g")
		        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
				
			// extra svg to clip the graph and x axis as they transition in and out
		    var graph = g.append("svg")
		        .attr("width", width)
		        .attr("height", height + margin.top + margin.bottom);	
			
		    var xAxis = d3.svg.axis().scale(x).orient("bottom");
		    var axis = graph.append("g")
		        .attr("class", "x axis")
		        .attr("transform", "translate(0," + height + ")")
		        .call(x.axis=xAxis);
			 
		    g.append("g")
		        .attr("class", "y axis")
		        .call(d3.svg.axis().scale(y).orient("left"));
			 
			var path1 = graph.append("g")
				.append("path")
				.data([data1])
				.attr("class", "line1");
				
			var path2 = graph.append("g")
				.append("path")
				.data([data2])
				.attr("class", "line2");
				
			var path3 = graph.append("g")
				.append("path")
				.data([data3])
				.attr("class", "line3");
				
			var path4 = graph.append("g")
				.append("path")
				.data([data4])
				.attr("class", "line4");
			

			tick();
				
		    function tick() {

				t++;
				
				// push
				updateData(data1);
				updateData(data2);
				updateData(data3);
				updateData(data4);

		        // update the domains
		        x.domain([t - n + 2 , t]);
				
		        // redraw the lines
		        graph.select(".line1").attr("d", line).attr("transform", null);
				graph.select(".line2").attr("d", line).attr("transform", null);
				graph.select(".line3").attr("d", line).attr("transform", null);
				graph.select(".line4").attr("d", line).attr("transform", null);
				
		        // slide the line left
				path1
					.transition()
					.duration(duration)
		            .ease("linear")
					.attr("transform", "translate(" + x(t-n+1) + ")");
					
				path2
					.transition()
					.duration(duration)
		        .ease("linear")
					.attr("transform", "translate(" + x(t-n+1) + ")");
					
				path3
					.transition()
					.duration(duration)
		        .ease("linear")
					.attr("transform", "translate(" + x(t-n+1) + ")");
				
				path4
					.transition()
					.duration(duration)
		        .ease("linear")
					.attr("transform", "translate(" + x(t-n+1) + ")");
		            
				 // slide the x-axis left
		        axis.transition()
		            .duration(duration)
		            .ease("linear")
		            .call(xAxis)
					.each("end", tick);


		        data1.shift();
				data2.shift();
				data3.shift();
				data4.shift();
				
		    }		
	}

