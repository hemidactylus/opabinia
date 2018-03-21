// CONSTANTS
var minBarHeight = 4; // min height of the plot line
var zeroAxisHeight=2; // height of the line marking the zero axis
var zeroAxisColor="#006000";

var gwidth=600;       // viewport size of the svg
var gheight=330;      // (these must match the size on the html!)

// margins and plot geometry
var margin = {top: 20, right: 30, bottom: 40, left: 50},
    width = gwidth - margin.left - margin.right,
    height = gheight - margin.top - margin.bottom;

var fullDay=1000.0*86400;
var oneHour=1000.0*3600.0;

// in-plot gutters
var fpGutter=oneHour*0.15; // space between plotted lines and plot area, horiz.
var xGutter=180000;   // gutter between plot area and canvas borders
var lineYGutter=3;
var histoYGutter=1;
var histogramXGap=0.14; // fraction of the full-bar-width to leave empty (sum of the sides)

var historyXGutter=0.5*fullDay;
var historyYGutter = 8;
var historyBarGap=0.14;

// curves to plot
var countsCurveSets=[
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
// history bar series to plot
historyBarSets=[
  {
    'name': 'max',
    'color': 'black',
    'index': 0,
    'title': 'Max in'
  },
  {
    'name': 'ins',
    'color': 'cyan',
    'index': 1,
    'title': 'In hits'
  },
  {
    'name': 'abscount',
    'color': '#C0C0C0',
    'index': 2,
    'title': 'Hits'
  },
  {
    'name': 'count',
    'color': 'red',
    'index': 3,
    'title': 'Bias'
  }
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
var formatDate=function(tstamp){
  var date = new Date(tstamp);
  var year = date.getFullYear();
  var month = "0" + (date.getMonth()+1);
  var day = "0" + date.getDate();
  return year + '/' + month.substr(-2) + '/' + day.substr(-2);
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

var displayMessage = function(elem,msg) {
  var msgBox=elem.append("g")
  var msgText=msgBox
    .append("text")
    .text(msg);
  var tx=0.5*(width-msgText.node().getBBox().width);
  var ty=0.5*(height-msgText.node().getBBox().height);
  msgBox
    .attr("transform","translate("+tx+","+ty+")");
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

// main function to issue the plot
d3.json(reqUrl,function(error,data){
  if(error != undefined){
    displayMessage(chartBody,"An error occurred.");
  } else {
    // general setup of canvas and axes
    var y = d3.scaleLinear()
      .range([0,height]);
    var x = d3.scaleTime()
      .range([0, width]);
    var xAxis = d3.axisBottom()
      .scale(x);
    var yAxis = d3.axisLeft()
      .scale(y);
    var xaxis=chartBody.append("g")
      // .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")");
    var yaxis=chartBody.append("g")
      // .attr("class", "y axis")
      .attr("transform", "translate(0,0)");

    if (plotType == "History") {
      plotData=data.history;
      if (plotData.length<1) {
        displayMessage(chartBody,"No data to plot.")
      } else {
        // a quadruplet of histo bars per each day
        addAxisLabels(chartBody,"Day","Counts");
        var time_min=d3.min(plotData.map( function(d){return d.jtimestamp;} ));
        var time_max=d3.max(plotData.map( function(d){return d.jtimestamp;} ));
        var time_extent=time_max-time_min;
        var y_max=d3.max(plotData.map(
          function(d) {return d3.max(
            historyBarSets.map(function(bs) {return d[bs.name];} )
          );}
        ));
        var y_min=d3.min(plotData.map(
          function(d) {return d3.min(
            historyBarSets.map(function(bs) {return d[bs.name];} )
          );}
        ));

        y.domain([y_max+historyYGutter,y_min-historyYGutter]);
        x.domain([time_min-historyXGutter-0.5*fullDay, time_max+historyXGutter+0.5*fullDay]);
        var barsWidth=(1-historyBarGap)*(x(time_max)-x(time_min))/(1.0*plotData.length-1.0);
        var barsLeftGap=(0.5*historyBarGap)*(x(time_extent)-x(0))/(1.0*plotData.length-1);
        //
        chartBody
          .append("g")
          .attr("transform","translate("+x(time_min-0.5*fullDay-historyXGutter)+","+(y(0)-0.5*zeroAxisHeight)+")")
          .append("rect")
          .attr("width",x(time_max+0.5*fullDay+historyXGutter)-x(time_min-0.5*fullDay-historyXGutter))
          .attr("height",zeroAxisHeight)
          .attr("fill",zeroAxisColor);
        //
        for (ihistory=0;ihistory<historyBarSets.length;ihistory++){
          tHistory=historyBarSets[ihistory];
          histoMaxInSel=chartBody.selectAll("."+tHistory.name+" g").data(plotData);
          histoMaxInBars=histoMaxInSel
              .enter()
              .append("g")
              .attr("transform", function(d) {
                return "translate("
                  +(x(d.jtimestamp-0.5*fullDay)+(ihistory*barsWidth/4.0)+barsLeftGap)
                  +","
                  +(d[tHistory.name]>0? (y(d[tHistory.name])-y(y_max+historyYGutter)) : y(0) )
                  +")";
              } );
          histoMaxInBars.append("rect")
              // .attr("class","lineclass")
              .style("fill",tHistory.color)
              .attr("width",function(d) {return 0.25*barsWidth;})
              .attr("height",function(d) { return y(0)-y(Math.abs(d[tHistory.name])); })
              .attr("fill-opacity",0.66);
          histoMaxInBars.append("title")
              .text(function(d) { return  formatDate(d.jtimestamp) + ": "+tHistory.title+" " + d[tHistory.name]; });
        }

        xaxis.call(xAxis);
        yaxis.call(yAxis);

      }
  } else if (plotType == "Hits") {
      var plotData=data.histogram;
      console.log(plotData);
      if (plotData.length<1) {
        displayMessage(chartBody,"No data to plot.");
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
              return "translate("+x(d.jtimestamp-(0.5-0.5*histogramXGap)*tSpan)
                +","+y(0)+")";
            } );
        cbars.append("rect")
            // .attr("class","lineclass")
            .style("fill","red")
            .attr("width",function(d) {return width*((1-histogramXGap)*d.span/time_extent);})
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
              return "translate("+x(d.jtimestamp-(0.5-0.5*histogramXGap)*tSpan)
                +","+(y(d.ins)-y(abs_y_max+histoYGutter))+")";
            } );
        cbars.append("rect")
            // .attr("class","lineclass")
            .style("fill","cyan")
            .attr("width",function(d) {return width*((1-histogramXGap)*d.span/time_extent);})
            .attr("height",function(d) { return y(0)-y(d.ins); })
            .attr("fill-opacity",0.66);
        cbars.append("title")
            .text(function(d) { return  formatTime(d.jtimestamp) + ": influx " + d.ins; });

        xaxis.call(xAxis);
        yaxis.call(yAxis);

      }
    } else { // plotType == 'Counts'
      if (data.points.length<2) {
        displayMessage(chartBody,"No data to plot.");
      } else {
        // restrict the range to the time of interest (depends on data!)
        var plotData=data.points.reverse()
        addAxisLabels(chartBody,"Time","Counts");

        // we add a 'span' property to each point to measure its horiz-extent
        for(var i=0; i<plotData.length-1; i++){
          plotData[i].span=plotData[i+1].jtimestamp-plotData[i].jtimestamp;
        }
        if ((plotData[plotData.length-1].jtimestamp+fpGutter)>data.now) {
          plotData[plotData.length-1].span=data.now-plotData[plotData.length-1].jtimestamp;
        } else {
          plotData[plotData.length-1].span=fpGutter;
        }
        plotData[0].jtimestamp=plotData[1].jtimestamp-fpGutter;
        plotData[0].span=fpGutter;
        // x axis max/min
        var time_min=d3.min(plotData.map( function(d){return d.jtimestamp;} ));
        var time_max=d3.max(plotData.map( function(d){return d.jtimestamp+d.span;} ));
        var time_extent=time_max-time_min;
        // y max and min across curves
        var y_min=d3.min(countsCurveSets.map(function(cv) {
          return d3.min(plotData.map(function(d){
            return d[cv.name]
          }));
        }));
        var y_max=d3.max(countsCurveSets.map(function(cv) {
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

        for(i=0; i<countsCurveSets.length;i++){
          var tCurve = countsCurveSets[i];
          crectasel=chartBody.selectAll("."+tCurve.name+" g").data(plotData);
          crectas=crectasel
              .enter()
              .append("g")
              .attr("transform", function(d) {return "translate("+x(d.jtimestamp)
                +","+(y(d[tCurve.name])-0.5*barHeight)+")"; } )
              .attr("class",function(d){return "c_"+d.jtimestamp; });

          crectas.append("rect")
              // .attr("class","lineclass")
              .style("fill",tCurve.color)
              .attr("width",function(d) {return x(d.jtimestamp+d.span)-x(d.jtimestamp);})
              .attr("height",barHeight)
              .attr("fill-opacity",0.66);
          crectas.append("title")
              .text(function(d) { return  d[tCurve.name] + " ("+tCurve.title+") "
                                          + formatTimeInterval(d.jtimestamp,d.span); });

          crectas.on('mouseenter',function(d){
              d3.selectAll("g .c_"+d.jtimestamp)
                  .selectAll('rect')
                  .style('stroke','gold')
                  .style('stroke-width', 2);
          });
          crectas.on('mouseleave',function(d){
              d3.selectAll("g .c_"+d.jtimestamp)
                  .selectAll('rect')
                  .style('stroke-width', 0);
          });
        }
        xaxis.call(xAxis);
        yaxis.call(yAxis);

      }
    }
  }
});
