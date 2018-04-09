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
from bokeh.models.glyphs import VBar
from bokeh.palettes import Plasma9

import os




data = df.HDFStore('shake_me\data\earthquake2.hdf')
# csv_files = next(os.walk('data'))[2]
earthquake_df = df.concat([
    data.get_storer(f).read().groupby(['year']).size().reset_index(name='count')
    for f in data.keys()
])

count_eq = ColumnDataSource(dict(
    year=[str(value) for value in earthquake_df['year'].tolist()],
    count=earthquake_df['count'].tolist()
))

TOOLS = "box_select,lasso_select,help"
hover = HoverTool(tooltips=[
    ('annee', '@year'),
    ('nombre', '@count')],
     mode='vline')
histo = figure(
    x_range=[str(value) for value in earthquake_df['year'].tolist()],
    plot_height=800,
    plot_width=1300,
    title="eq Counts",
    tools=[hover, TOOLS]
)
histo.vbar(
    source=count_eq,
    x='year',
    top='count',
    width=1,
    fill_color="#b3de69"
)
histo.xgrid.grid_line_color = None
histo.y_range.start = 0


years = [1950, 2018]

source_data_format = dict(x=[], y=[], mag=[], year=[], detail=[], title=[])

source_micro = ColumnDataSource(data=source_data_format)
source_tres_mineur = ColumnDataSource(data=source_data_format)
source_mineur = ColumnDataSource(data=source_data_format)
source_leger = ColumnDataSource(data=source_data_format)
source_modere = ColumnDataSource(data=source_data_format)
source_fort = ColumnDataSource(data=source_data_format)
source_tres_fort = ColumnDataSource(data=source_data_format)
source_majeur = ColumnDataSource(data=source_data_format)
source_devastateur = ColumnDataSource(data=source_data_format)

# display data
TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

hover = HoverTool(tooltips=[
    ("nom", "@title"),
    ("annee", "@year"),
    ("magnitude", "@mag"),
    ("impact", "@detail")
])

plot = figure(
    title="Shake me !",
    tools=[hover, TOOLS],
    plot_width=1000,
    plot_height=800,
    active_scroll="wheel_zoom",
    output_backend="webgl"
)

label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
plot.add_layout(label)

plot.add_tile(STAMEN_TERRAIN_RETINA)




plot.circle(x='x', y='y', source=source_micro, size=2, color=Plasma9[8], alpha=1, legend="Micro", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_tres_mineur, size=3, color=Plasma9[7], alpha=1, legend="Tres mineur", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_mineur, size=4, color=Plasma9[6], alpha=1, legend="Mineur", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_leger, size=5, color=Plasma9[5], alpha=1, legend="Leger", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_modere, size=6, color=Plasma9[4], alpha=1, legend="Modere", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_fort, size=7, color=Plasma9[3], alpha=1, legend="Fort", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_tres_fort, size=8, color=Plasma9[2], alpha=1, legend="Tres fort", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_majeur, size=9, color=Plasma9[1], alpha=1, legend="Majeur", line_width=0.1, line_color="white")
plot.circle(x='x', y='y', source=source_devastateur, size=10, color=Plasma9[0], alpha=1, legend="Devastateur", line_width=0.1, line_color="white")



class DataToBokeh(object):

    def __init__(self, year, input_data_path, detail_value):

        self._year = year
        self._input_data_path = input_data_path
        self._detail_value = detail_value
        # OUTPUT_DATA_PATH = '.\shake_me\data'

    def run(self):
        earthquake_df = self._read_hdf_file()
        source = self._create_datasource_output(earthquake_df)
        return source

    def _read_hdf_file(self):
        # df_eq = df.HDFStore('%s\earthquake2.hdf' % (self._input_data_path))
        df_eq = df.read_hdf(
            '%s\earthquake2.hdf' % (self._input_data_path),
            key='y%s' % self._year
            # where="detail=['%s']" % self._detail_value
        )

        df_eq = df_eq.query("detail == '%s'" % self._detail_value)
        # df_eq = df_eq.get_storer('y%s' % self._year).read()
        # df_eq = df_eq.loc[
        #     (df_eq['mag'] > 0) & (df_eq['detail'] == self._detail_value)
        # ].copy()

        return df_eq

    def _create_datasource_output(self, dataframe):

        x = dataframe['x'].tolist()
        y = dataframe['y'].tolist()
        mag = dataframe['mag'].tolist()
        year = dataframe['year'].tolist()
        detail = dataframe['detail'].tolist()
        title = dataframe['title'].tolist()

        return dict(
            x=x,
            y=y,
            mag=mag,
            year=year,
            detail=detail,
            title=title
    )

def slider_update(attrname, old, new):
    year = slider.value
    label.text = str(year)

    detail_list = {
        'Micro': source_micro,
        'Tres mineur': source_tres_mineur,
        'Mineur': source_mineur,
        'Leger': source_leger,
        'Modere': source_modere,
        'Fort': source_fort,
        'Tres fort': source_tres_fort,
        'Majeur': source_majeur,
        'Devastateur': source_devastateur
    }
    for detail_value, source in detail_list.items():
        source.data = DataToBokeh(year, '.\shake_me\data', detail_value).run()

# Add the slider
slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")
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
    row(plot),
    row(slider),
    row(button_past, button_next),
    row(histo)
)

curdoc().add_root(layout)
curdoc().title = "Map_test"
