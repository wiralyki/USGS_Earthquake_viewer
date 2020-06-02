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


function get_data_from_usgs(start_date, end_date) {
    var url_build = `http://127.0.0.1:5000/api/v1/mapdata?start_date=${start_date}&end_date=${end_date}&min_lat=${map.getBounds().getSouth()}&max_lat=${map.getBounds().getNorth()}&min_lng=${map.getBounds().getWest()}&max_lng=${map.getBounds().getEast()}`;

    $.ajax({
        url: url_build,
        async: true,
        success: function (result) {

            const mapData = result["map_data"];
            const chartData = result["chart_data"];

            objectsMapper(mapData)
            objectsCharted(chartData)
        },
    })

}


function objectsMapper(data) {
    // console.log(data)
    data.forEach(function (feature, i) {
        feature.LatLng = new L.LatLng(
            feature.y,
            feature.x
        )
    })

    data.forEach(function (feature, i) {
        feature.time = dateToSecs(new Date(feature.time))
    })
    var data_grouped = {}
    data_grouped = data.reduce((data, feature) => {
        data[feature.mag_cat] = data[feature.mag_cat] || [];
        data[feature.mag_cat].push(feature);
        return data;
    }, {});

    // console.log(data_grouped)
    /* Initialize the SVG layer */
    var svgLayer = L.svg();
    svgLayer.addTo(map);

    // order svg group
    var svg = d3.select("#map").select("svg").attr("id", "svgMap")
    var mag_reordered = Object.keys(magContents());
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
            .attr("time", function (d, i) {
                return d.time;
            })
            .attr("class", "displayed")

        var time_between_each_object = 100;
        var fade_speed = 1000;
        $("svg").find("g").each(function (i, path) {
            $(path).delay(time_between_each_object * i).fadeIn(fade_speed, function () {

            });
        })
    }
    var svgCircle = $("#map").find("circle")
    animateCircle(svgCircle)
}

function objectsCharted(chart_data) {
    var width = 900
    var height = 300

    function div_tootltip_content(d) {
        var div = document.createElement('div');
        div.setAttribute("class", "chart-tooltip-content")

        var title = document.createElement('h6');
        title.innerHTML = d.country
        div.append(title)

        document.createElement('h6');
        var listObject = document.createElement('ul');

        var listItem = document.createElement('li');
        listItem.innerHTML = "Minor: " + d.minor
        listObject.append(listItem);

        var listItem = document.createElement('li');
        listItem.innerHTML = "Light: " + d.light
        listObject.append(listItem);

        var listItem = document.createElement('li');
        listItem.innerHTML = "Moderate: " + d.moderate
        listObject.append(listItem);

        var listItem = document.createElement('li');
        listItem.innerHTML = "Strong: " + d.strong
        listObject.append(listItem);

        var listItem = document.createElement('li');
        listItem.innerHTML = "Major: " + d.major
        listObject.append(listItem);

        var listItem = document.createElement('li');
        listItem.innerHTML = "Great: " + d.great
        listObject.append(listItem);

        div.append(listObject)
        return div
    }

    function sum( obj, keys ) {
      var sum = 0;
      for( var el in obj ) {
        if(keys.includes(el)) {
          sum += parseFloat( obj[el] );
        }
      }
      return sum;
    }

    // chart_data.forEach(function (feature, i) {
    //     feature.count = sum(feature, Object.keys(magContents()))
    // })
    var data = chart_data

    var margin = {top: 20, right: 50, bottom: 30, left: 20};
    var width = width - margin.left - margin.right;
    var height = height - margin.top - margin.bottom - 50;
    var svg = d3.select("#chart")
        .append("svg")
        .attr("id", "svgChart")
        .attr("viewBox", `0 0 ${width} ${height}`)
    var g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleBand()
        .rangeRound([0, width])
        .paddingInner(0.05)
        .align(0.1);

    var y = d3.scaleLinear().rangeRound([height, 0]);

    var z = d3.scaleOrdinal()
        .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

    var columns = Object.keys(magContents());
    var keys = columns.reverse();

    data.sort(function(a, b) { return b.total - a.total; });
    x.domain(data.map(function(d,i) { return i; }));
    y.domain([0, d3.max(data, function(d) { return d.count; })]).nice();
    z.domain(keys);


    g.append("g")
        .selectAll("g")
        .data(d3.stack().keys(keys)(data))
        .enter().append("g")
          .attr("class", function(d) { return d.key; })
        .selectAll("rect")
        .data(function(d) { return d; })
        .enter().append("rect")
            .attr("x", function(d,i) { return x(i); })
            .attr("y", function(d) { return y(d[1]); })
            .attr("height", function(d) { return y(d[0]) - y(d[1]); })
            .attr("width", x.bandwidth())
            .style("opacity", "0")
            .on("click", function(d) {
                $(".chart-tooltip").remove()
                map.flyToBounds([
                  [d.data.bounds[3], d.data.bounds[2]],
                  [d.data.bounds[1], d.data.bounds[0]],
                ])

            })
            .on("mouseover", function(d) {
                // Define the div for the tooltip
                var div = d3.select("body").append("div")
                    .attr("class", "chart-tooltip")
                    .style("opacity", 0);
                div.transition()
                    .duration(200)
                div.html(div_tootltip_content(d.data).outerHTML)
                    .style("opacity", 1)
                    .style("position", "absolute")
                    .style("fill", "ghostwhite")
            })
            .on("mouseout", function(d) {
                $('.chart-tooltip').remove()
            })
            .on('mousemove', function() {
                d3.select('.chart-tooltip')
                    .style("position", "absolute")
                    .style('left', (d3.event.pageX + 30) + 'px')
                    .style('top', (d3.event.pageY - 100) + 'px')
            });

    // Animation
    g.selectAll("rect")
      .transition()
      .duration(800)
      .style("opacity", "1")
      .delay(function(d,i){console.log(i) ; return(i*100)})

    g.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickFormat(function(d,i) { return data[i].country}))
      .selectAll("text")
        .attr("y", 0)
        .attr("x", 9)
        .attr("dy", ".35em")
        .attr("font-size", 8)
        .attr("transform", "rotate(45)")
        .style("text-anchor", "start");


    g.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(y).ticks(null, "s"))
    .append("text")
        .attr("x", 2)
        .attr("y", y(y.ticks().pop()) + 0.5)
        .attr("dy", "0.32em")
        .attr("fill", "#000")
        .attr("font-weight", "bold")
        .attr("text-anchor", "start")
        .text("Earthquakes");

    var legend = g.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 10)
        .attr("text-anchor", "end")
    .selectAll("g")
    .data(keys.reverse())
    .enter().append("g")
        .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

    legend.append("rect")
        .attr("x", width - 19)
        .attr("width", 19)
        .attr("height", 19)
        .attr("fill", z)
        .attr("class", function(d) { return d; });

    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9.5)
        .attr("dy", "0.32em")
        .text(function(d) { return d; });

}

function transform_coords(d) {
    var coor = map.latLngToLayerPoint(d.LatLng);
       return "translate(" +
           coor.x + "," +
           coor.y + ")";
}

function magContents() {

    return {
        'great': {
            "r": 50,
        },
        'major': {
            "r": 40,
        },
        'strong': {
            "r": 30,
        },
        'moderate': {
            "r": 24,
        },
        'light': {
            "r": 12,
        },
        'minor': {
            "r": 5,
        },
    }
}



function createLegend(width, height) {
    var svgNS = "http://www.w3.org/2000/svg";
    var divis = 2
    var svgTextELementSep = 70
    var svgELementSep = 20

    var legend_item_svg = document.createElementNS(svgNS,'svg');
    legend_item_svg.setAttribute("viewBox", `0 -50 ${width} ${width}`)
    legend_item_svg.setAttribute("class", `svgLegend`)

    var mag_reordered = Object.keys(magContents());

    mag_reordered.forEach(function (mag_cat, index) {
        // group
        var group = document.createElementNS(svgNS,'g');
        group.setAttribute("class", mag_cat)

        // dot
        var svgCircle = document.createElementNS(svgNS,"circle");
        svgCircle.setAttributeNS(null,"cx", width / divis);
        svgCircle.setAttributeNS(null,"cy", height / divis + index * svgELementSep);
        group.append(svgCircle);
        // text
        var svgText = document.createElementNS(svgNS,"text");
        svgText.setAttribute("x", width / divis + svgTextELementSep);
        svgText.setAttribute("y", height / divis + index * svgELementSep);
        svgText.setAttribute("alignment-baseline", "middle")
        svgText.innerHTML = mag_cat
        group.append(svgText);

        legend_item_svg.append(group)
    })
    $('#legend-content').append(legend_item_svg)
}


$('.dropdown-menu a').click(function () {
    $("#button-time-scale").text($(this).text());
});

// todo api output...
var dates = ["2000-01-01", "2000-02-01", "2000-03-01", "2000-04-01", "2000-05-01", "2000-06-01", "2000-07-01", "2000-08-01", "2000-09-01", "2000-10-01", "2000-11-01", "2000-12-01", "2001-01-01"];


// Update the current slider value (each time you drag the slider handle)
$("#timeSlider").change(function() {

    var timeScaleMode = $('.dropdown-time-scale').find("button").text()
    if (timeScaleMode === "Monthly") {

        var currentDate = dates[this.value]
        $("#slider-value").text(currentDate);
        var currentDateInt = dateToSecs(currentDate)
        var nextCurrentDate = new Date(currentDateInt).setMonth(new Date(currentDateInt).getMonth() + 1);
        filterCircleByScaleTimeMode(currentDateInt, nextCurrentDate)

    } else if (timeScaleMode === "Daily") {
        var currentDate = parseInt(this.value)
        var timeScaleDayValue = 86400000
        var nextCurrentDate = currentDate + timeScaleDayValue
        filterCircleByScaleTimeMode(currentDate, nextCurrentDate)
    }

})


function filterCircleByScaleTimeMode(currentDate, nextCurrentDate) {
    var svgCircle = $("#map").find("circle")
    svgCircle.toArray().forEach(function(feature, index) {
        $(feature).attr("class", "hidden")
        $(feature).empty()
    })

    var svgCircleToDisplay = svgCircle.filter(index => parseInt($(svgCircle[index]).attr('time')) >= currentDate && parseInt($(svgCircle[index]).attr('time')) < nextCurrentDate);
    svgCircleToDisplay.toArray().forEach(function(feature, index) {
        $(feature).attr("class", "displayed")
    })
    animateCircle(svgCircleToDisplay)
}

function animateCircle(features) {
    features.toArray().forEach(function(feature, index) {
        var feature_mag = $(feature)[0].__data__.mag_cat;

        if (['great', 'major', 'strong'].includes(feature_mag)) {
            var rAnim =document.createElementNS("http://www.w3.org/2000/svg", 'animate');
            rAnim.setAttribute("attributeName","r");
            rAnim.setAttribute("from",magContents()[feature_mag].r);
            rAnim.setAttribute("to", magContents()[feature_mag].r * 1.5);
            rAnim.setAttribute("dur","1.5s");
            rAnim.setAttribute("begin","0s");
            rAnim.setAttribute("repeatCount","indefinite");
            $(feature).append(rAnim)

            var opacityAnim =document.createElementNS("http://www.w3.org/2000/svg", 'animate');
            opacityAnim.setAttribute("attributeName","opacity");
            opacityAnim.setAttribute("from","1");
            opacityAnim.setAttribute("to","0");
            opacityAnim.setAttribute("dur","1.5s");
            opacityAnim.setAttribute("begin","0s");
            opacityAnim.setAttribute("repeatCount","indefinite");
            $(feature).append(opacityAnim)
        }
    })
}


$("#submit-dates").click(function() {
    $("#map").attr('loaded', "ok")

    // clean svg
    $("#map").find("svg").remove()
    $("#chart").find("svg").remove()

    // Init slider
    let start_date = $("#from-date-input").val();
    let end_date = $("#to-date-input").val();
    initializeSlider(start_date, end_date);

    // get data
    get_data_from_usgs(start_date, end_date);
    if ($(".svgLegend").length === 0) {
        createLegend(20, 40)
    }

    // activate slider dialog if necessary
    var timeScaleMode = $('.dropdown-time-scale').find("button").text()
    if (timeScaleMode !== "Interval selected") {
        $(".slider-dates-container").css('pointer-events', "auto")
        $(".slider-dates-container").css('opacity', 1)
    }

});


map.on("moveend", function(s){

    $("#map").find("svg").remove();
    $("#chart").find("svg").remove();
    if ($("#map").attr('loaded') === "ok") {
        // only if data has been already added



        // get data
        let start_date = $("#from-date-input").val();
        let end_date = $("#to-date-input").val();
        get_data_from_usgs(start_date, end_date);

        // create legend only if it does not exist
        if ($(".svgLegend").length === 0) {
            createLegend(20, 40)
        };
    }
});


function initializeSlider(start_date, end_date) {

    var timeScaleMode = $('.dropdown-time-scale').find("button").text()

    if (timeScaleMode === "Daily") {
        let timeScaleDayValue = 86400000
        $("#timeSlider").attr('min', start_date)
        $("#timeSlider").attr('max', end_date)
        $("#timeSlider").attr('step', timeScaleDayValue)
        $("#timeSlider").attr('value', start_date)
        $("#slider-value").text(secsToDate(start_date));
    }

    if (timeScaleMode === "Monthly") {
        $("#timeSlider").attr('min', 0)
        $("#timeSlider").attr('max', dates.length - 1)
        $("#timeSlider").attr('step', 1)
        $("#timeSlider").attr('value', 0)
        $("#slider-value").text(dates[0]);
    }
}


function dateToSecs(date) {
    var date_int = Date.parse(date)
    return date_int
}

function secsToDate(date_int) {
    var date = new Date(date_int).toISOString().split("T")[0]
    return date
}

function findMonthDaysFromDate(date) {
    var days_month = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
    return days_month
}








