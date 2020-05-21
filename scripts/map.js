var map = L.map('map', {
    renderer: L.canvas()
    }
).setView([46.505954, 7.108154], 6);

var background_map = L.tileLayer('https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png', {
    attribution: 'By <a href="https://github.com/yruama42/USGS_Earthquake_viewer">Yruama42</a>. Source: <a href="https://earthquake.usgs.gov/fdsnws/event/1/">USGS</a>. Map tiles by <a href="http://stamen.com">Stamen Design</a>, <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    minZoom: 0,
    maxZoom: 20,
    id: 'stamen'

})

background_map.addTo(map)

var earthquakeLayersCl1 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl2 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl3 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl4 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl5 = new L.FeatureGroup().addTo(map);
var earthquakeLayersCl6 = new L.FeatureGroup().addTo(map);

let range = (start, end) => Array.from(Array(end + 1).keys()).slice(start);

var removeMarkers = function() {
    map.eachLayer(function(layer) {

    if (layer.options.id != "stamen") {
        map.removeLayer(layer)
        }
    });
}

var magContentsValues = magContents()


// var legend = L.control({position: 'topright'});
// legend.onAdd = function (map) {

    var legend_div = document.createElement('div');
    legend_div.setAttribute("id", "legend");
    legend_div.setAttribute("class","legend-container col-sm-4")

    var start_y_pos = 40
    var y_pos_increment = 30

    // count_categories to compute legend heigh
    const categories_prop = Object.getOwnPropertyNames(magContentsValues);
    var cat_count = categories_prop.length
    var legend_heigh = start_y_pos + (y_pos_increment * cat_count) + 10

    var legend_svg = `
        <svg id="svgLegend" width="160" height="${legend_heigh}">
        <polygon points="0,0 160,0 160,${legend_heigh} 0,${legend_heigh} 0,0" fill="white" />
        <text x="5" y="20" font-weight="bold">Magnitude</text>
    `

    for (var cat in magContentsValues) {
        var values = magContentsValues[cat];
        var color = values['color']
        var size = values['size']
        var fontWeight = values['font-weight']
        legend_svg += `
            <circle cx="40" cy="`+  start_y_pos +`" r="`+  size +`" stroke="black" stroke-width="0.5" fill="`+  color +`" />
            <text class="legend_pointer" id="`+  cat +`" font-weight="bold" onclick='highlightedModeSelecting("`+  cat +`")' x="70" y="`+  start_y_pos +`" transform="translate(8,4)">`+  cat +`</text>
        `
        start_y_pos += 30
    }



    legend_div.innerHTML = legend_svg;
    $('#content').append(legend_div)
    // document.body.appendChild(legend_div);

    // return legend_div;
// };
// legend.addTo(map);



// get_usgs_eq_data
function get_usgs_eq_data(start_year, end_year, layersgroup) {

    // load data on his layer group
    var magIntervals = magContents()

    const http = new XMLHttpRequest()
    console.log(map.getBounds().getSouth())
    http.open("GET", "https://earthquake.usgs.gov/fdsnws/event/1/query?"+ 'format=geojson' + "&starttime=" + start_year + "&endtime=" + end_year +     "&minlatitude=" + map.getBounds().getSouth() + "&maxlatitude=" + map.getBounds().getNorth() + "&minlongitude=" + map.getBounds().getWest() + "&maxlongitude=" + map.getBounds().getEast())

    http.send(null);
    http.onload = function (e) {
        if (http.status === 200 && http.readyState === 4 ) {
            var response = JSON.parse(http.responseText);
            console.log(response)

            response['features'].forEach(function (feature, _) {

                for (var category in magIntervals) {

                    var values = magIntervals[category]

                    if (feature.properties.mag >= values['intervals'][0] && feature.properties.mag < values['intervals'][1]) {

                        featuresPrepared = L.geoJSON(
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
// get_usgs_eq_data //

// Timeline interaction
getDataAddMarkers = function(label, map) {
    var dates = []
    for (i = 0; i < 12; i++) {
        var firstDate = new Date(label, i+1, 1);
        var lastDate = new Date(label, i+1, 0);
        console.log("aaaa", label)

            first_date_month = firstDate.getMonth()
            first_date_day = firstDate.getDate()
            first_date_year = firstDate.getFullYear()

            last_date_month = lastDate.getMonth() + 1
            last_date_day = lastDate.getDate()
            last_date_year = lastDate.getFullYear()
        dates.push([
          [first_date_year, first_date_month, first_date_day].join('-'),
          [last_date_year, last_date_month, last_date_day].join('-')
        ])
    }

    // clear all layers from last year
    //earthquakeLayers.clearLayers()
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
            "size": 3,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [0, 4.0],
            "grouplayer": earthquakeLayersCl1
        },
        'Light': {
            "color": "#fee08b",
            "size": 5,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [4.0, 5.0],
            "grouplayer": earthquakeLayersCl2
        },
        'Moderate': {
            "color": "#fdae61",
            "size": 9,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [5.0, 6.0],
            "grouplayer": earthquakeLayersCl3
        },
        'Strong': {
            "color": "#f46d43",
            "size": 15,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [6.0, 7.0],
            "grouplayer": earthquakeLayersCl4
        },
        'Major': {
            "color": "#d73027",
            "size": 23,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [7.0, 8.0],
            "grouplayer": earthquakeLayersCl5
        },
        'Great': {
            "color": "#a50026",
            "size": 33,
            "font-weight": "bold",
            "fillOpacity":1,
            "opacity":1,
            "intervals": [8.0, 9999.0],
            "grouplayer": earthquakeLayersCl6
        }
    }
}

function highlightedModeSelecting(category) {
    var textSvgCategory = document.getElementById("svgLegend").getElementById(category)

    groupLayerSelected = magContentsValues[category]["grouplayer"]

    if (textSvgCategory.getAttribute("font-weight") == "bold") {

        textSvgCategory.setAttribute("font-weight", "normal");
        groupLayerSelected.setStyle({fillOpacity:0,opacity:0})

    } else {
        textSvgCategory.setAttribute("font-weight", "bold");
        groupLayerSelected.setStyle({fillOpacity:1,opacity:1})

    }
}

function highlightedModechecking () {
    console.log('test')
    var magIntervals = magContents()
    for (var category in magIntervals) {

        var textSvgCategory = document.getElementById("svgLegend").getElementById(category)

        groupLayerSelected = magContentsValues[category]["grouplayer"]

        if (textSvgCategory.getAttribute("font-weight") == "bold") {
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


var output = document.getElementById("demo");
// output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  // output.innerHTML = this.value;
  getDataAddMarkers(this.value, "value", map, "exclamation")
}

map.on("moveend", function(s){
    getDataAddMarkers(slider.value, "value", map, "exclamation");
});