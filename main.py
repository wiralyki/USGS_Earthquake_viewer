# display USA earthquakes

# TODO add comments

import grequests

import calendar
import datetime

import geojson
import json

from shapely.geometry import shape

import geopandas as gpd
import pandas as pd

from geopandas import GeoDataFrame
from geopandas import GeoSeries

from bokeh.io import curdoc
from bokeh.io import output_file
from bokeh.layouts import column
from bokeh.layouts import layout
from bokeh.layouts import row
from bokeh.layouts import widgetbox
from bokeh.models import Button
from bokeh.models import ColumnDataSource
from bokeh.models import CustomJS
from bokeh.models import GeoJSONDataSource
from bokeh.models import HoverTool
from bokeh.models import Label
from bokeh.models import LinearColorMapper
from bokeh.models import Slider
from bokeh.plotting import ColumnDataSource
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA

def get_month_start_end_date(year, month):
    first_month_day = datetime.date(year, month, 1)
    last_month_day = first_month_day.replace(day = calendar.monthrange(first_month_day.year, first_month_day.month)[1])
    return (first_month_day, last_month_day)


def get_month_start_end_date_from_period(start_year, end_year):

    dates_list = []

    year_range = end_year - start_year + 1
    current_year = start_year

    while current_year <= end_year:
        dates_list.extend([
            get_month_start_end_date(current_year, month_nb)
            for month_nb in range(1, 13)
            if datetime.datetime(current_year, month_nb, 1) <= datetime.datetime.now()  
        ])
        current_year += 1

    return dates_list


dates_to_requests = get_month_start_end_date_from_period(2017, 2018)

earthquake_gdfs = []

for start_date, end_date in dates_to_requests:
# for data in requests_data:
    
    results = grequests.get("https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s" % (
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    ))
    
    requests_data = grequests.imap([results])
    requests_data = [f for f in requests_data][0]
    earthquakes =  gpd.GeoDataFrame.from_features(
        geojson.loads(
            json.dumps(requests_data.json())
        )['features']
    )
    earthquakes = earthquakes.loc[earthquakes.alert != None]
    earthquakes = earthquakes[['geometry', 'mag', 'type']]
    earthquakes['year'] = int(start_date.strftime("%Y-%m-%d").split('-')[0])
    earthquake_gdfs.append(earthquakes.head(100))

earthquake_gdf = pd.concat(earthquake_gdfs)
earthquake_gdf.crs = {'init' :'epsg:4326'}
earthquake_gdf = earthquake_gdf.to_crs({'init': 'epsg:3857'})
earthquake_gdf['x'] = earthquake_gdf.geometry.apply(lambda geom: geom.x)
earthquake_gdf['y'] = earthquake_gdf.geometry.apply(lambda geom: geom.y)
earthquake_gdf = earthquake_gdf[['x', 'y', 'mag', 'year']]

earthquake_gdf_dict_by_year = {}
years = list(set(earthquake_gdf['year'].values))
for year in years:
    earthquake_gdf_dict_by_year[year] = earthquake_gdf.loc[earthquake_gdf.year == year].copy().to_dict('series')

# earthquake_bokeh = ColumnDataSource(data=earthquake_gdf_dict_by_year[years[0]])
earthquake_bokeh = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[]))

source = earthquake_bokeh
# source = ColumnDataSource(pd.DataFrame(columns=['x','y','type','mag','year']))


# display data
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
plot = figure(title="Shake me !", tools=TOOLS, 
           plot_width=600, plot_height=400, active_scroll = "wheel_zoom", output_backend="webgl")

label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
plot.add_layout(label)

plot.add_tile(STAMEN_TERRAIN_RETINA)

color_mapper = LinearColorMapper(palette='Magma256', low=min(earthquake_gdf['mag']), high=max(earthquake_gdf['mag']))
plot.circle(
    x='x',
    y='y',
    source=source,
    size=10,
    color={'field': 'mag', 'transform': color_mapper},
    alpha=0.5,
    legend="earthquake"
)

# Add the slider

slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")
def slider_update(attrname, old, new):
    year = slider.value
    df = earthquake_gdf_dict_by_year[year]
    label.text = str(year)
    earthquake_bokeh.data = dict(
        x=df['x'].tolist(),
        y=df['y'].tolist(),
        mag=df['mag'].tolist(),
        year=df['year'].tolist()
    )
slider.on_change('value', slider_update)

layout = row(plot, slider)

curdoc().add_root(layout)
curdoc().title = "Thomas est un trou du cul"
