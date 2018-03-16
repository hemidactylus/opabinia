// CONSTANTS
var minBarHeight = 4; // min height of the plot line
var zeroAxisHeight=1;
var zeroAxisColor="black";

var gwidth=600;       // viewport size of the svg
var gheight=330;      // (these must match the size on the html!)

// margins and plot geometry
var margin = {top: 20, right: 30, bottom: 40, left: 50},
    width = gwidth - margin.left - margin.right,
    height = gheight - margin.top - margin.bottom;

// in-plot gutters
var fpGutter=3600000; // space between plotted lines and plot area, horiz.
var xGutter=180000;   // 
var lineYGutter=3;
var histoYGutter=1;
var histoXGutterFrac=0.14; // fraction of the full-bar-width to leave empty (sum of the sides)

// curves to plot
var curves=[
  {
    "name": "abscount",
    "color": "black",
    "title": "Hits"
  },
  {
    "name": "ins",
    "color": "red",
    "title": "In hits"
  },
  {
    "name": "count",
    "color": "cyan",
    "title": "People in"
  },
];

// UTILITY FUNCTIONS
var formatTime=function(tstamp){
  var date = new Date(tstamp);
  // Hours part from the timestamp
  var hours = date.getHours();
  // Minutes part from the timestamp
  var minutes = "0" + date.getMinutes();
  // Seconds part from the timestamp
  var seconds = "0" + date.getSeconds();
  // Will return time in 10:30:23 format
  return hours + ':' + minutes.substr(-2) + ':' + seconds.substr(-2);
}
var formatTimeInterval=function(tstamp,span){
  var t2=span+tstamp
  return formatTime(tstamp)+" - "+formatTime(t2);
}

var addAxisLabels = function(elem,xlabel,ylabel) {
  elem.append("text")
    // .attr("class","axislabel")
    .attr("x", width)
    .attr("y",height)
    .attr("dx", "-10px")
    .attr("dy", "34")
    .style("text-anchor", "end")
    .text(xlabel);

  elem.append("text")
    // .attr("class","axislabel")
    .attr("transform", "rotate(-90)")
    .attr("y", -20)
    .attr("dy", "-0.71em")
    .style("text-anchor", "end")
    .text(ylabel);
}

// creation and resizing of the plot window
var chart = d3.select(".chart")
  // these four are the only one on the actual SVG (outside of a viewbox)
  .attr("width", "100%")
  .attr("height", "400px")
  .style("background-color", "#707070")
  .append("g")
  // for mouse events
  .attr("pointer-events", "all")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var chartBody = chart.append("g")
  .attr("id","chartBody")
  .attr("clip-path", "url(#clip)");

d3.json(reqUrl,function(error,data){
  if(error != undefined){
    var errg=chartBody.append("g")
    var errt=errg
      .append("text")
      .text("An error occurred.");
    var tx=0.5*(width-errt.node().getBBox().width);
    var ty=0.5*(height-errt.node().getBBox().height);
    errg
      .attr("transform","translate("+tx+","+ty+")");
  } else {

    var y = d3.scaleLinear()
      .range([0,height]);
    var x = d3.scaleTime()
      .range([0, width]);
    var xAxis = d3.axisBottom()
      .scale(x);
    var yAxis = d3.axisLeft()
      .scale(y);
    var xaxis=chartBody.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")");
    var yaxis=chartBody.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(0,0)");

    if (plotType == "History") {
     var errg=chartBody.append("g")
      var errt=errg
        .append("text")
        .text("Plot not supported.");
      var tx=0.5*(width-errt.node().getBBox().width);
      var ty=0.5*(height-errt.node().getBBox().height);
      errg
        .attr("transform","translate("+tx+","+ty+")");
  } else if (plotType == "Hits") {
      var plotData=data.histogram;
      console.log(plotData);
      if (plotData.length<1) {
        var errg=chartBody.append("g")
        var errt=errg
          .append("text")
          .text("No data to plot.");
        var tx=0.5*(width-errt.node().getBBox().width);
        var ty=0.5*(height-errt.node().getBBox().height);
        errg
          .attr("transform","translate("+tx+","+ty+")");
      } else {
        // double histogram for hits
        var tSpan=plotData[0].span;
        addAxisLabels(chartBody,"Time","Flux");
        var time_min=d3.min(plotData.map(function(d){return d.jtimestamp;}));
        var time_max=d3.max(plotData.map(function(d){return d.jtimestamp;}));
        var time_extent=time_max+tSpan-time_min;
        // y extent
        var abs_y_max=d3.max(plotData.map(
          function(d){return d3.max([Math.abs(d.ins),Math.abs(d.outs)]);}
        ));
        //
        y.domain([abs_y_max+histoYGutter,-abs_y_max-histoYGutter]);
        var y_extent = 2*(abs_y_max+histoYGutter);
        x.domain([time_min-0.5*tSpan,time_max+0.5*tSpan]);
        var barHeight=minBarHeight;
        //
        chartBody
          .append("g")
          .attr("transform","translate("+x(time_min-0.5*tSpan)+","+(y(0)-0.5*zeroAxisHeight)+")")
          .append("rect")
          .attr("width",x(time_max+0.5*tSpan)-x(time_min-0.5*tSpan))
          .attr("height",zeroAxisHeight)
          .attr("fill",zeroAxisColor);
        // outs
        cbarsel=chartBody.selectAll(".outs g").data(plotData);
        cbars=cbarsel
            .enter()
            .append("g")
            .attr("transform", function(d) {
              return "translate("+x(d.jtimestamp-(0.5-0.5*histoXGutterFrac)*tSpan)
                +","+y(0)+")";
            } );
        cbars.append("rect")
            // .attr("class","lineclass")
            .style("fill","red")
            .attr("width",function(d) {return width*((1-histoXGutterFrac)*d.span/time_extent);})
            .attr("height",function(d) { return y(0)-y(d.outs); })
            .attr("fill-opacity",0.66);
        cbars.append("title")
            .text(function(d) { return  formatTime(d.jtimestamp) + ": outflux " + d.outs; });
        // ins
        cbarsel=chartBody.selectAll(".ins g").data(plotData);
        cbars=cbarsel
            .enter()
            .append("g")
            .attr("transform", function(d) {
              return "translate("+x(d.jtimestamp-(0.5-0.5*histoXGutterFrac)*tSpan)
                +","+(y(d.ins)-y(abs_y_max+histoYGutter))+")";
            } );
        cbars.append("rect")
            // .attr("class","lineclass")
            .style("fill","cyan")
            .attr("width",function(d) {return width*((1-histoXGutterFrac)*d.span/time_extent);})
            .attr("height",function(d) { return y(0)-y(d.ins); })
            .attr("fill-opacity",0.66);
        cbars.append("title")
            .text(function(d) { return  formatTime(d.jtimestamp) + ": influx " + d.ins; });

        xaxis.call(xAxis);
        yaxis.call(yAxis);

      }
    } else { // plotType == 'Counts'
      if (data.points.length<2) {
        var errg=chartBody.append("g")
        var errt=errg
          .append("text")
          .text("No data to plot.");
        var tx=0.5*(width-errt.node().getBBox().width);
        var ty=0.5*(height-errt.node().getBBox().height);
        errg
          .attr("transform","translate("+tx+","+ty+")");
      } else {
        // restrict the range to the time of interest (depends on data!)
        var plotData=data.points.reverse()
        addAxisLabels(chartBody,"Time","Counts");

        // we add a 'span' property to each point to measure its horiz-extent
        for(var i=0; i<plotData.length-1; i++){
          plotData[i].span=plotData[i+1].jtimestamp-plotData[i].jtimestamp;
        }
        plotData[plotData.length-1].span=data.now-plotData[plotData.length-1].jtimestamp;
        plotData[0].jtimestamp=plotData[1].jtimestamp-fpGutter;
        plotData[0].span=fpGutter;
        // x axis max/min
        var time_min=d3.min(plotData.map( function(d){return d.jtimestamp;} ));
        var time_max=d3.max(plotData.map( function(d){return d.jtimestamp+d.span;} ));
        var time_extent=time_max-time_min;
        // y max and min across curves
        var y_min=d3.min(curves.map(function(cv) {
          return d3.min(plotData.map(function(d){
            return d[cv.name]
          }));
        }));
        var y_max=d3.max(curves.map(function(cv) {
          return d3.max(plotData.map(function(d){
            return d[cv.name]
          }));
        }));

        y.domain([y_max+lineYGutter,y_min-lineYGutter]);
        var y_extent = y_max+lineYGutter-y_min+lineYGutter;
        x.domain([time_min-xGutter,time_max+xGutter]);

        var unitHeight = height/y_extent;
        var barHeight = d3.max([minBarHeight,unitHeight])

        chartBody
          .append("g")
          .attr("transform","translate("+x(time_min-lineYGutter)+","+(y(0)-0.5*zeroAxisHeight)+")")
          .append("rect")
          .attr("width",x(time_max+lineYGutter)-x(time_min-lineYGutter))
          .attr("height",zeroAxisHeight)
          .attr("fill",zeroAxisColor);

        for(i=0; i<curves.length;i++){
          var tCurve = curves[i];
          crectasel=chartBody.selectAll("."+tCurve.name+" g").data(plotData);
          crectas=crectasel
              .enter()
              .append("g")
              .attr("transform", function(d) {return "translate("+x(d.jtimestamp)
                +","+(y(d[tCurve.name])-0.5*barHeight)+")"; } );
          crectas.append("rect")
              // .attr("class","lineclass")
              .style("fill",tCurve.color)
              .attr("width",function(d) {return width*(d.span/time_extent);})
              .attr("height",barHeight)
              .attr("fill-opacity",0.66);
          crectas.append("title")
              .text(function(d) { return  d[tCurve.name] + " ("+tCurve.title+") "
                                          + formatTimeInterval(d.jtimestamp,d.span); });
        }
        xaxis.call(xAxis);
        yaxis.call(yAxis);

      }
    }
  }
});
