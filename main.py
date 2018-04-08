# display USA earthquakes

import geojson


from shapely.geometry import shape

import geopandas as gdf
import pandas as df

from geopandas import GeoDataFrame
from geopandas import GeoSeries
from bokeh.models.widgets import CheckboxGroup
from bokeh.io import curdoc
from bokeh.io import output_file
from bokeh.layouts import column
from bokeh.layouts import layout
from bokeh.layouts import row
from bokeh.layouts import widgetbox
from bokeh.models import Button

from bokeh.models import HoverTool
from bokeh.models import Label
from bokeh.models import LinearColorMapper
from bokeh.models import Slider
from bokeh.plotting import ColumnDataSource
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA

from bokeh.palettes import Plasma9

import os

OUTPUT_DATA_PATH = '.\data'

csv_files = next(os.walk('.\data'))[2]
earthquake_df = df.concat(
    [
        df.read_csv('%s\%s' % (OUTPUT_DATA_PATH, input_file))
        for input_file in csv_files
    ], ignore_index=True
)
earthquake_df = earthquake_df.loc[earthquake_df['mag'] > 0].copy()


years = [min(earthquake_df.year), max(earthquake_df.year)]


source_micro = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_tres_mineur = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_mineur = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_leger = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_modere = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_fort = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_tres_fort = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_majeur = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))
source_devastateur = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[], description=[]))

# display data
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
plot = figure(title="Shake me !", tools=TOOLS,
           plot_width=1000, plot_height=800, active_scroll="wheel_zoom", output_backend="canvas")

label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
plot.add_layout(label)

plot.add_tile(STAMEN_TERRAIN_RETINA)

plot.circle(x='x', y='y', source=source_micro, size=2, color=Plasma9[8], alpha=1, legend="Micro")
plot.circle(x='x', y='y', source=source_tres_mineur, size=3, color=Plasma9[7], alpha=1, legend="Tres mineur")
plot.circle(x='x', y='y', source=source_mineur, size=4, color=Plasma9[6], alpha=1, legend="Mineur")
plot.circle(x='x', y='y', source=source_leger, size=5, color=Plasma9[5], alpha=1, legend="Leger")
plot.circle(x='x', y='y', source=source_modere, size=6, color=Plasma9[4], alpha=1, legend="Modere")
plot.circle(x='x', y='y', source=source_fort, size=7, color=Plasma9[3], alpha=1, legend="Fort")
plot.circle(x='x', y='y', source=source_tres_fort, size=8, color=Plasma9[2], alpha=1, legend="Tres fort")
plot.circle(x='x', y='y', source=source_majeur, size=9, color=Plasma9[1], alpha=1, legend="Majeur")
plot.circle(x='x', y='y', source=source_devastateur, size=10, color=Plasma9[0], alpha=1, legend="Devastateur")


# Add the slider
slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")

def slider_update(attrname, old, new):
    year = slider.value
    df_micro = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Micro')]
    df_tres_mineur = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Tres mineur')]
    df_mineur = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Mineur')]
    df_leger = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Leger')]
    df_modere = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Modere')]
    df_fort = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Fort')]
    df_tres_fort = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Tres fort')]
    df_majeur = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Majeur')]
    df_devastateur = earthquake_df.loc[(earthquake_df['year'] == year) & (earthquake_df['description'] == 'Devastateur')]

    label.text = str(year)
    source_micro.data = dict(
        x=df_micro['x'].tolist(),
        y=df_micro['y'].tolist(),
        mag=df_micro['mag'].tolist(),
        year=df_micro['year'].tolist(),
        description=df_micro['description'].tolist()
    )
    source_tres_mineur.data = dict(
        x=df_tres_mineur['x'].tolist(),
        y=df_tres_mineur['y'].tolist(),
        mag=df_tres_mineur['mag'].tolist(),
        year=df_tres_mineur['year'].tolist(),
        description=df_tres_mineur['description'].tolist()
    )
    source_mineur.data = dict(
        x=df_mineur['x'].tolist(),
        y=df_mineur['y'].tolist(),
        mag=df_mineur['mag'].tolist(),
        year=df_mineur['year'].tolist(),
        description=df_mineur['description'].tolist()
    )
    source_tres_fort.data = dict(
        x=df_tres_fort['x'].tolist(),
        y=df_tres_fort['y'].tolist(),
        mag=df_tres_fort['mag'].tolist(),
        year=df_tres_fort['year'].tolist(),
        description=df_tres_fort['description'].tolist()
    )
    source_leger.data = dict(
        x=df_leger['x'].tolist(),
        y=df_leger['y'].tolist(),
        mag=df_leger['mag'].tolist(),
        year=df_leger['year'].tolist(),
        description=df_leger['description'].tolist()
    )
    source_modere.data = dict(
        x=df_modere['x'].tolist(),
        y=df_modere['y'].tolist(),
        mag=df_modere['mag'].tolist(),
        year=df_modere['year'].tolist(),
        description=df_modere['description'].tolist()
    )
    source_fort.data = dict(
        x=df_fort['x'].tolist(),
        y=df_fort['y'].tolist(),
        mag=df_fort['mag'].tolist(),
        year=df_fort['year'].tolist(),
        description=df_fort['description'].tolist()
    )
    source_fort.data = dict(
        x=df_fort['x'].tolist(),
        y=df_fort['y'].tolist(),
        mag=df_fort['mag'].tolist(),
        year=df_fort['year'].tolist(),
        description=df_fort['description'].tolist()
    )
    source_majeur.data = dict(
        x=df_majeur['x'].tolist(),
        y=df_majeur['y'].tolist(),
        mag=df_majeur['mag'].tolist(),
        year=df_majeur['year'].tolist(),
        description=df_majeur['description'].tolist()
    )
    source_devastateur.data = dict(
        x=df_devastateur['x'].tolist(),
        y=df_devastateur['y'].tolist(),
        mag=df_devastateur['mag'].tolist(),
        year=df_devastateur['year'].tolist(),
        description=df_devastateur['description'].tolist()
    )


slider.on_change('value', slider_update)

def past_year_update():
    year = slider.value - 1
    if year < years[0]:
        year = years[-1]
    slider.value = year

def next_year_update():
    year = slider.value + 1
    if year > years[-1]:
        year = years[0]
    slider.value = year

button_next = Button(label='Next Year', width=60)
button_next.on_click(next_year_update)

button_past = Button(label='Past Year', width=60)
button_past.on_click(past_year_update)

plot.legend.click_policy="hide"

layout = column(
    plot,
    row(slider, button_past, button_next)
)

curdoc().add_root(layout)
curdoc().title = "Map_test"
