var background_map = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}.png', {
    attribution: 'By <a href="https://github.com/yruama42/USGS_Earthquake_viewer">Yruama42</a>. Source: <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS</a>. Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    minZoom: 0,
    maxZoom: 20,
});

var map = L.map(
    'map',
    {
        preferCanvas: true,
        renderer: L.canvas()
    }
).addLayer(background_map).setView([44.896741, 4.932861], 6)
setTimeout(function () { map.invalidateSize() }, 800);


/* Initialize the SVG layer */
var svgLayer = L.svg();
svgLayer.addTo(map);

var chart_data = []
var chart_data_grouped = []

function get_data_from_usgs(start_date, end_date) {
    var url_build = `http://127.0.0.1:5000/api/v1/mapdata?start_date=${start_date}&end_date=${end_date}&min_lat=${map.getBounds().getSouth()}&max_lat=${map.getBounds().getNorth()}&min_lng=${map.getBounds().getWest()}&max_lng=${map.getBounds().getEast()}`;

    $.ajax({
        url: url_build,
        async: true,
        success: function (result) {

            var mapData = result["map_data"];
            var chartData = result["chart_data"];

            objectsMapper(mapData)
            // objectsCharted(chartData)
        },
    })

}


function objectsMapper(data) {
    data.forEach(function (feature, i) {
        feature.LatLng = new L.LatLng(
            feature.y,
            feature.x
        )
    })

    let data_grouped = data.reduce((data, feature) => {
        data[feature.mag_cat] = data[feature.mag_cat] || [];
        data[feature.mag_cat].push(feature);
        return data;
    }, {});

    // order svg group
    var svg = d3.select("#map").select("svg")
    var mag_reordered = magContents();
    mag_reordered.forEach(function (mag_cat, index) {
        var g = svg.append("g")
        g.attr("class", mag_cat)
    })

    for (var mag_cat in data_grouped) {
        var data_group = data_grouped[mag_cat]

        var g = svg.select("." + mag_cat);
        var _ = g.selectAll("LatLng")
            .data(data_group)
            .enter().append("circle")
            .attr("transform", function (d, i) {
                return transform_coords(d);
            })

        var time_between_each_object = 100;
        var fade_speed = 1000;
        $("svg").find("g").each(function (i, path) {
            $(path).delay(time_between_each_object * i).fadeIn(fade_speed, function () {

            });
        })
    }
}


function objectsCharted(data) {
    // set the dimensions of the canvas
    var margin = {top: 20, right: 20, bottom: 70, left: 40},
        width = 600 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;


    // set the ranges
    var x = d3.scale.ordinal().rangeRoundBands([0, width], .05);

    var y = d3.scale.linear().range([height, 0]);

    // define the axis
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")


    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10);


    // add the SVG element
    var svg = d3.select("chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");


    // load the data
    d3.json("data.json", function(error, data) {


    // scale the range of the data
    x.domain(data.map(function(d) { return d.Letter; }));
    y.domain([0, d3.max(data, function(d) { return d.Freq; })]);

    // add axis
    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", "-.55em")
      .attr("transform", "rotate(-90)" );

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 5)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Frequency");


    // Add bar chart
    svg.selectAll("bar")
      .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.Letter); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.Freq); })
      .attr("height", function(d) { return height - y(d.Freq); });

    });
}


function transform_coords(d) {
    var coor = map.latLngToLayerPoint(d.LatLng);
       return "translate(" +
           coor.x + "," +
           coor.y + ")";
}


function magContents() {

    return ['great', 'major', 'strong', 'moderate', 'light', 'minor']
}

function createLegend(width, height) {
    var svgNS = "http://www.w3.org/2000/svg";
    var divis = 2
    var width = 30;
    var height = 30;

    // legend
    var legend_div = document.createElement('div');
    legend_div.setAttribute("id", "legend-content");
    legend_div.setAttribute("class","legend-container row")

    // create legend item div
    var legend_item_div = document.createElement('div');
    legend_item_div.setAttribute("id", "legend-item-div");
    legend_item_div.setAttribute("class","col-sm")

    var mag_reordered = magContents();
    mag_reordered.forEach(function (mag_cat, index) {


        // create symbol div
        var legend_item_symbol = document.createElement('div');
        legend_item_symbol.setAttribute("class","legend-item-symbol col-sm")
        // svg
        var legend_item_svg = document.createElementNS(svgNS,'svg');
        legend_item_svg.setAttribute("height", width)
        legend_item_svg.setAttribute("width", width)
        legend_item_svg.setAttribute("class", mag_cat)
        // dot
        var svgCircle = document.createElementNS(svgNS,"circle");
        svgCircle.setAttributeNS(null,"cx", width / divis);
        svgCircle.setAttributeNS(null,"cy", height / divis);
        legend_item_svg.append(svgCircle);
        // text
        var svgText = document.createElementNS(svgNS,"text");
        svgText.setAttribute("x", (width / divis) + width * 2.5);
        svgText.setAttribute("y", height / divis);
        svgText.setAttribute("alignment-baseline", "middle")
        svgText.innerHTML = mag_cat
        legend_item_svg.append(svgText);


        legend_item_symbol.append(legend_item_svg)
        legend_item_div.append(legend_item_symbol)
        legend_div.append(legend_item_div)
    })
    $('#legend').append(legend_div)
}




// slider processing
var slider = document.getElementById("mySlider");
slider.max = 2020
slider.min = 1980
// slider.value = 2000



// output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
// slider.oninput = function() {
//     var output = $("from-date-input");
//
//   $("#slider-value").text(this.value);
//   $("svg").find("g").remove();
//   getDataAddMarkers(this.value, map)
// }

createLegend(1, 1)

$("submit").click(function(){
  alert("The paragraph was clicked.");

   var start_date = $("#from-date-input").attr("value");
   var end_date = $("#to-date-input").attr("value");

   get_data_from_usgs(start_date, end_date);


});


map.on("moveend", function(s){
    $("svg").find("g").remove();
    var start_date = $("#from-date-input").attr("value");
    var end_date = $("#to-date-input").attr("value");

    get_data_from_usgs(start_date, end_date);

});


function toDateTime(secs) {
    var t = new Date(1970, 0, 1); // Epoch
    t.setSeconds(secs);
    return t;
}








