
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

var earthquakeLayersCl1 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl2 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl3 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl4 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl5 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl6 = new L.FeatureGroup().addTo(map);

var magContentsValues = magContents()

// legend
var legend_div = document.createElement('div');
legend_div.setAttribute("id", "legend");
legend_div.setAttribute("class","legend-container row")

for (var cat in magContentsValues) {
    var values = magContentsValues[cat];
    var color = values['color']
    var size = values['size']
    var font_weight = values['font-weight']

    var legend_item_symb = document.createElement('div');
    legend_item_symb.setAttribute("class","legend-item-symb col-sm-6")
    var legend_item_svg = create_circle(size, size, "svg" + cat, {"fill": color})
    legend_item_symb.append(legend_item_svg)

    var legend_item_value = document.createElement('div');
    legend_item_value.setAttribute("class","legend-item-value col-sm-6")
    legend_item_value.setAttribute("id", cat);
    var value_item = document.createElement("a");
    legend_item_value.setAttribute("style", "font-weight:" + font_weight);


    value_item.innerHTML = cat
    legend_item_value.append(value_item)

    legend_div.append(legend_item_symb)
    legend_div.append(legend_item_value)
}
$('#side-bar').append(legend_div)



function create_circle(width, height, id_name, style) {
    var svgNS = "http://www.w3.org/2000/svg";
    var divis = 2

    var svg = document.createElementNS(svgNS,'svg');
    svg.setAttribute("id", id_name)
    svg.setAttribute("height", height)
    svg.setAttribute("width", width)


    var svg_item = document.createElementNS(svgNS,"circle");

    svg_item.setAttributeNS(null,"cx"    , width / divis);
    svg_item.setAttributeNS(null,"cy"    , height / divis);
    svg_item.setAttributeNS(null,"r"     , width > height ? height / divis : width / divis);
    for (var property in style) {
        svg_item.setAttributeNS(null, property, style[property]);
    }
    svg.append(svg_item);

    return svg
}




// get_usgs_eq_data
function get_usgs_eq_data(start_year, end_year) {

    // load data on his layer group
    var magIntervals = magContents()

    const http = new XMLHttpRequest()
    http.open(
        "GET",
        "https://earthquake.usgs.gov/fdsnws/event/1/query?"+ 'format=geojson' + "&starttime=" + start_year + "&endtime=" + end_year +  "&minlatitude=" + map.getBounds().getSouth() + "&maxlatitude=" + map.getBounds().getNorth() + "&minlongitude=" + map.getBounds().getWest() + "&maxlongitude=" + map.getBounds().getEast(),
    )
    http.send(null);
    http.onload = function (e) {
        if (http.status === 200 && http.readyState === 4 ) {
            var response = JSON.parse(http.responseText);

            response['features'].forEach(function (feature, _) {

                for (var category in magIntervals) {
                    var values = magIntervals[category]
                    if (feature.properties.mag >= values['intervals'][0] && feature.properties.mag < values['intervals'][1]) {
                        featuresPrepared = L.geoJson(
                            [feature],
                            {
                                onEachFeature: marker_popup,
                                pointToLayer: function(feature, latlng) {
                                    return L.circleMarker(
                                        latlng,
                                        styleTemplate(values['size'], values['color'], values['fillOpacity'], values['opacity'])
                                    )
                                }
                            }
                        )
                        values['grouplayer'].addLayer(featuresPrepared)
                    };
                };
            })
        }
        //check legend selections
        highlightedModechecking()
    }

}

function marker_popup(feature, layer) {
        // ugly
        content = "<b>Name:</b> " + feature.properties.title + "<br><b>magnitude:</b> " + feature.properties.mag + "<br><b>Date:</b> " + new Date(feature.properties.time);
        layer.bindPopup(
            content,
            {
                closeOnClick: false,
                autoClose: false
            }
        );

        layer.on('click', function(event){
            layer.openPopup();
        });
}

function styleTemplate(radius_value, fillecolor_value, fillOpacity_value, opacity_value) {
    return {
        radius: radius_value,
        fillColor: fillecolor_value,
        opacity: opacity_value,
        fillOpacity: opacity_value,
        color: 'black',
        weight: 1
    };
}

// Timeline interaction
getDataAddMarkers = function(label, map) {
    var dates = []
    for (i = 0; i < 12; i++) {
        var firstDate = new Date(label, i+1, 1);
        var lastDate = new Date(label, i+1, 0);

        dates.push([
          [firstDate.getFullYear(), firstDate.getMonth(), firstDate.getDate()].join('-'),
          [lastDate.getFullYear(), lastDate.getMonth() + 1, lastDate.getDate()].join('-')
        ])
    }

    // clear all layers from last year
    earthquakeLayersCl1.clearLayers()
    earthquakeLayersCl2.clearLayers()
    earthquakeLayersCl3.clearLayers()
    earthquakeLayersCl4.clearLayers()
    earthquakeLayersCl5.clearLayers()
    earthquakeLayersCl6.clearLayers()

    var layerGroups = {
        "Minor": earthquakeLayersCl1,
        "Light": earthquakeLayersCl2,
        "Moderate": earthquakeLayersCl3,
        "Strong": earthquakeLayersCl4,
        "Major": earthquakeLayersCl5,
        "Great": earthquakeLayersCl6,
    }

    // query data on each month between selected year

    for (var i in dates) {
        get_usgs_eq_data(dates[i][0], dates[i][1], map, layerGroups)
    }
}

function magContents() {

    return {
        'Minor': {
            "color": "#d9ef8b",
            "size": 6,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [0, 4.0],
            "grouplayer": earthquakeLayersCl1
        },
        'Light': {
            "color": "#fee08b",
            "size": 10,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [4.0, 5.0],
            "grouplayer": earthquakeLayersCl2
        },
        'Moderate': {
            "color": "#fdae61",
            "size": 18,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [5.0, 6.0],
            "grouplayer": earthquakeLayersCl3
        },
        'Strong': {
            "color": "#f46d43",
            "size": 30,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [6.0, 7.0],
            "grouplayer": earthquakeLayersCl4
        },
        'Major': {
            "color": "#d73027",
            "size": 46,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [7.0, 8.0],
            "grouplayer": earthquakeLayersCl5
        },
        'Great': {
            "color": "#a50026",
            "size": 66,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [8.0, 9999.0],
            "grouplayer": earthquakeLayersCl6
        }
    }
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
        highlightedModechecking()
    });
});

function highlightedModechecking () {
    var magIntervals = magContents()
    for (var category in magIntervals) {

        var textSvgCategory = $("#" + category)

        groupLayerSelected = magContentsValues[category]["grouplayer"]

        if (textSvgCategory.css("font-weight") == 700) {

            groupLayerSelected.setStyle({fillOpacity:1,opacity:1})

        } else {

            groupLayerSelected.setStyle({fillOpacity:0,opacity:0})
        }
    }
}

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
  getDataAddMarkers(this.value, "value", map, "exclamation")
}

map.on("moveend", function(s){
    getDataAddMarkers(slider.value, "value", map, "exclamation");
});

