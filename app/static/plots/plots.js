
// creation and resizing of the plot window
var gwidth=600;
var gheight=360;
var margin = {top: 20, right: 30, bottom: 40, left: 50},
    width = gwidth - margin.left - margin.right,
    height = gheight - margin.top - margin.bottom
var chart = d3.select(".chart")
  // these four are the only one on the actual SVG (outside of a viewbox)
  .attr("width", "100%")
  .attr("height", "400px")
  //.attr("width", width + margin.left + margin.right)
  //.attr("height", height + margin.top + margin.bottom)
  .style("background-color", "#C0C0C0")
  .append("g")
  // see mouse-events below
  .attr("pointer-events", "all")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var y = d3.scaleLinear()
        .range([0,height])
        // .range([height,0])
var x = d3.scaleTime()
        .range([0, width]);
var xAxis = d3.axisBottom()
    .scale(x)
var yAxis = d3.axisLeft()
    .scale(y);

var xaxis=chart.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")");
// xaxis.append("text")
//     .attr("class","axislabel")
//     .attr("x", width)
//     .attr("dx", "-10px")
//     .attr("dy", "34")
//     .style("text-anchor", "end")
//     .text("Time");
var yaxis=chart.append("g")
    .attr("class", "y axis")
    .attr("transform", "translate(0,0)");
// yaxis.append("text")
//     .attr("class","axislabel")
//     .attr("transform", "rotate(-90)")
//     .attr("y", -20)
//     .attr("dy", "-0.71em")
//     .style("text-anchor", "end")
//     .text("Number");
var chartBody = chart.append("g")
    .attr("id","chartBody")
    .attr("clip-path", "url(#clip)");

d3.json("http://localhost:5000/datacounters/"+reqDate,function(error,data){
    // restrict the range to the time of interest (depends on data!)
    var plotData=data.points.reverse()
    // we add a 'span' property of each point
    for(var i=0; i<plotData.length-1; i++){
      plotData[i].span=plotData[i+1].jtimestamp-plotData[i].jtimestamp;
    }
    plotData[plotData.length-1].span=data.now-plotData[plotData.length-1].jtimestamp;
    var fpGutter=3600000;
    var xGutter=180000;
    var yGutter=3;
    plotData[0].jtimestamp=plotData[1].jtimestamp-fpGutter;
    plotData[0].span=fpGutter;
    var time_min=d3.min(plotData.map( function(d){return d.jtimestamp;} ))
    var time_max=d3.max(plotData.map( function(d){return d.jtimestamp+d.span;} ))
    var y_min1=d3.min(plotData.map( function(d){return d.abscount;} ))
    var y_max1=d3.max(plotData.map( function(d){return d.abscount;} ))
    var y_min2=d3.min(plotData.map( function(d){return d.ins;} ))
    var y_max2=d3.max(plotData.map( function(d){return d.ins;} ))
    var y_max=d3.max([y_max1,y_max2]);
    var y_min=d3.min([y_min1,y_min2]);
    var time_extent=time_max-time_min;

    var unitheight = height / (y_max-y_min+1);

    y.domain([y_max+yGutter,y_min-yGutter]);
    var y_extent = y_max+yGutter-y_min+yGutter;
    x.domain([time_min-xGutter,time_max+xGutter]);

    // var rectasel = chartBody.selectAll("g");
    // rectasel.remove();

    // // we now re-compute the d3 select to add new items
    rectasel1=chartBody.selectAll(".abscount g").data(plotData);

    chartBody
      .append("g")
      .attr("transform","translate("+x(time_min)+","+y(0+0.5)+")")
      .append("rect")
      .attr("width",x(time_max)-x(time_min))
      .attr("height",height/y_extent)
      .attr("fill","white")

    rectas1=rectasel1
        .enter()
        .append("g")
        .attr("transform", function(d) {return "translate("+x(d.jtimestamp)
          +","+y(d.abscount+0.5)+")"; } );
    rectas1.append("rect")
        .attr("class",function(d){return "lineclass";})
        .attr("width",function(d) {return width*(d.span/time_extent);})
        .attr("height",function(d){return height/y_extent;})
        .attr("fill-opacity",function(d){return 0.5;});
    // rectas.append("text")
    //     .attr("class",function(d){return d.value<0?"nonumberlabel":"numberlabel";})
    //     .attr("x", function(d){return 0.5*(x(d.end)-x(d.start));})
    //     .attr("y", 0)
    //     .attr("dy",function(d){return d.value<0?"22.0pt":(d.value<90?"-0.8pt":"9.2pt");})
    //     .style("text-anchor", "middle")
    //     .text(function(d){return ((d.end-d.start)>MIN_LABELED_DURATION)?valueLabel(d):""});
    rectas1.append("title")
        .text(function(d) { return d.abscount });

    rectasel2=chartBody.selectAll(".ins g").data(plotData);
    rectas2=rectasel2
        .enter()
        .append("g")
        .attr("transform", function(d) {return "translate("+x(d.jtimestamp)
          +","+y(d.ins+0.5)+")"; } );
    rectas2.append("rect")
        .attr("class",function(d){return "lineclass";})
        .attr("width",function(d) {return width*(d.span/time_extent);})
        .style("fill","red")
        .attr("height",function(d){return height/y_extent;})
        .attr("fill-opacity",function(d){return 0.5;});
    rectas2.append("title")
        .text(function(d) { return d.ins });

    rectasel3=chartBody.selectAll(".count g").data(plotData);
    rectas3=rectasel3
        .enter()
        .append("g")
        .attr("transform", function(d) {return "translate("+x(d.jtimestamp)
          +","+y(d.count+0.5)+")"; } );
    rectas3.append("rect")
        .attr("class",function(d){return "lineclass";})
        .attr("width",function(d) {return width*(d.span/time_extent);})
        .style("fill","green")
        .attr("height",function(d){return height/y_extent;})
        .attr("fill-opacity",function(d){return 0.5;});
    rectas3.append("title")
        .text(function(d) { return d.count });


    xaxis.call(xAxis);
    yaxis.call(yAxis);
});
