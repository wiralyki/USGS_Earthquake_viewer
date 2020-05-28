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
    var url_build = `https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=${start_date}&endtime=${end_date}&minlatitude=${map.getBounds().getSouth()}&maxlatitude=${map.getBounds().getNorth()}&minlongitude=${map.getBounds().getWest()}&maxlongitude=${map.getBounds().getEast()}`;

    const http = new XMLHttpRequest()
    http.open(
        "GET",
        url_build,
    )
    http.send(null);
    http.onload = function (e) {
        if (http.status === 200 && http.readyState === 4) {
            var data = JSON.parse(http.responseText)["features"];

            data.forEach(function (d, i) {
                d.LatLng = new L.LatLng(
                    d.geometry.coordinates[1],
                    d.geometry.coordinates[0]
                )
            })

            data.forEach(function (d, i) {
                d.title = set_svg_attr(d)["class"]
            })

            data.forEach(function (d, i) {
                d.r = set_svg_attr(d)["r"]
            })

            data.forEach(function (d, i) {
                d.place = d.properties.place
            })


            chart_data = $.merge(chart_data, data)

            let data_grouped = data.reduce((data, item) => {
                data[item.title] = data[item.title] || [];
                data[item.title].push(item);
                return data;
            }, {});

            // order svg group
            var svg = d3.select("#map").select("svg")
            for (var title in magContents()) {
                var g = svg.append("g")
                g.attr("class", title)
            }

            for (var title in data_grouped) {
                var data_group = data_grouped[title]

                var g = svg.select("." + title);
                var _ = g.selectAll("LatLng")
                    .data(data_group)
                    .enter().append("circle")
                    .attr("r", function (d, i) {
                        return set_svg_attr(d)["r"];
                    })
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
        return true
    }
}


// d3.selectAll("circle").on("mouseover", function(){
//     d3.select(this).raise();
// });

// var chart_data_grouped = []
// Timeline interaction

function getData(dates) {
    return new Promise(resolve => {
        for (var i in dates) {
            get_data_from_usgs(dates[i][0], dates[i][1]);
        }
        resolve(true)

    })
}

function getDataAddMarkers(label) {
    var dates = []
    for (i = 0; i < 12; i++) {

        var firstDate = new Date(label, i);
        var nextFirstDateMonth = new Date(label, i + 1);
        var lastDate = new Date(nextFirstDateMonth - 1);

        dates.push([
            [firstDate.getFullYear(), firstDate.getMonth() + 1, firstDate.getDate()].join('-'),
            [lastDate.getFullYear(), lastDate.getMonth() + 1, lastDate.getDate()].join('-')
        ])
    }
    // query data on each month between selected year
    // for (var i in dates) {
    //     get_data_from_usgs(dates[i][0], dates[i][1]);
    // }
    getData(dates).then(function (e) {
        chart_data_grouped = chart_data.reduce((feature, {place, title}) => {
            feature[place] = feature[place] || {place, title, count: 0};
            feature[place].count += 1;
            return feature;
        }, {})
        console.log(chart_data_grouped);
    })
}








console.log(chart_data)



function transform_coords(d) {
    var coor = map.latLngToLayerPoint(d.LatLng);
       return "translate(" +
           coor.x + "," +
           coor.y + ")";
}

function set_svg_attr(feature) {
    for (var title in magContents()){

        var interval_values = magContents()[title].interval
        if (feature.properties.mag >= interval_values[0] && feature.properties.mag < interval_values[1])
            return {"class": title, "r": magContents()[title].r}

     }
}


function magContents() {

    return {
        'great': {
            "r": 66,
            "interval": [8, 9999]
        },
        'major': {
            "r": 46,
            "interval": [7, 8]
        },
        'strong': {
            "r": 30,
            "interval": [6, 7]
        },
        'moderate': {
            "r": 18,
            "interval": [5, 6]
        },
        'light': {
            "r": 10,
            "interval": [4, 5]
        },
        'minor': {
            "r": 6,
            "interval": [0, 4]
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
slider.oninput = function() {
    var output = $("slider-value");

  $("#slider-value").text(this.value);
  $("svg").find("g").remove();
  getDataAddMarkers(this.value, map)
}

map.on("moveend", function(s){
    $("svg").find("g").remove();
    getDataAddMarkers(slider.value, map);
});

