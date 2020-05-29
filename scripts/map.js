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
    for (var mag_cat in magContents()) {
        var g = svg.append("g")
        g.attr("class", mag_cat)
    }

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


// d3.selectAll("circle").on("mouseover", function(){
//     d3.select(this).raise();
// });

// Timeline interaction







function transform_coords(d) {
    var coor = map.latLngToLayerPoint(d.LatLng);
       return "translate(" +
           coor.x + "," +
           coor.y + ")";
}


function magContents() {

    return {
        'great': {
            "r": 66,
        },
        'major': {
            "r": 46,
        },
        'strong': {
            "r": 30,
        },
        'moderate': {
            "r": 18,
        },
        'light': {
            "r": 10,
        },
        'minor': {
            "r": 6,
        },
    }
}


// legend
var legend_div = document.createElement('div');
legend_div.setAttribute("id", "legend");
legend_div.setAttribute("class","legend-container row")

// reorder key
var mag_reordered = Object.keys(magContents()).reverse();

mag_reordered.forEach(function (title, index) {
    var values = magContents()[title];
    var r = values['r']

    // circle
    var legend_item_symb = document.createElement('div');
    legend_item_symb.setAttribute("class","legend-item-symb col-sm-6")
    var legend_item_svg = create_circle(r, r, title)
    legend_item_symb.append(legend_item_svg)

    // text
    var legend_item_value = document.createElement('div');
    legend_item_value.setAttribute("class","legend-item-text col-sm-6")
    legend_item_value.setAttribute("id", title);
    var value_item = document.createElement("a");


    value_item.innerHTML = title
    legend_item_value.append(value_item)

    legend_div.append(legend_item_symb)
    legend_div.append(legend_item_value)
})
$('#legend').append(legend_div)




function create_circle(width, height, class_name) {
    var svgNS = "http://www.w3.org/2000/svg";
    var divis = 2

    var svg = document.createElementNS(svgNS,'svg');
    svg.setAttribute("class", class_name)
    svg.setAttribute("height", height)
    svg.setAttribute("width", width)

    var svg_item = document.createElementNS(svgNS,"circle");

    svg_item.setAttributeNS(null,"cx"    , width / divis);
    svg_item.setAttributeNS(null,"cy"    , height / divis);
    svg_item.setAttributeNS(null,"r"     , width > height ? height / divis : width / divis);
    svg.append(svg_item);

    return svg
}

$(document).ready(function() {
    $(".legend-item-value").click(function(){
        // console.log(this.id)
        // highlightedModeSelecting(this.id)
        var textSvgCategory = $("#" + this.id)
        groupLayerSelected = magContentsValues[this.id]["grouplayer"]
        console.log(textSvgCategory.css("font-weight"))
        if (textSvgCategory.css("font-weight") == 700) {
            textSvgCategory.css("font-weight", "normal");
        } else {
            textSvgCategory.css("font-weight", "bold");
        }
    });
});


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








