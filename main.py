# display USA earthquakes

import geojson


from shapely.geometry import shape

import geopandas as gdf
import pandas as df

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



import os
from shapely.wkt import loads
# import and format data csv in update

OUTPUT_DATA_PATH = '.\data'
OUTPUT_DATA_CRS = {'init': 'epsg:4326'}
OUTPUT_DATA_CRS_BOKEH = {'init': 'epsg:3857'}

csv_files = next(os.walk('.\data'))[2]
earthquake_df = df.concat(
    [
        df.read_csv('%s\%s' % (OUTPUT_DATA_PATH, input_file))
        for input_file in csv_files
    ], ignore_index=True
)
years = [min(earthquake_df.year), max(earthquake_df.year)]

source = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[]))

# display data
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
plot = figure(title="Shake me !", tools=TOOLS,
           plot_width=1000, plot_height=800, active_scroll = "wheel_zoom", output_backend="webgl")

label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
plot.add_layout(label)

plot.add_tile(STAMEN_TERRAIN_RETINA)

color_mapper = LinearColorMapper(palette='Magma256', low=min(earthquake_df['mag']), high=max(earthquake_df['mag']))
plot.circle(
    x='x',
    y='y',
    source=source,
    size=2,
    color={'field': 'mag', 'transform': color_mapper},
    alpha=1,
    legend="earthquake"
)

# Add the slider
slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")

def slider_update(attrname, old, new):
    year = slider.value
    df = earthquake_df.loc[earthquake_df['year'] == year]
    label.text = str(year)
    source.data = dict(
        x=df['x'].tolist(),
        y=df['y'].tolist(),
        mag=df['mag'].tolist(),
        year=df['year'].tolist()
    )
slider.on_change('value', slider_update)

layout = row(plot, slider)

curdoc().add_root(layout)
curdoc().title = "Map_test"
