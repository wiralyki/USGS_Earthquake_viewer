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

from bokeh.models.widgets import TextInput
from core.data_helper import ImportUsgsEarthquakeData


class GridsToBokeh(object):

    _TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    def __init__(self):

        source_data_formated = dict(mag=[], place=[], url=[], magType=[], type=[], title=[], x=[], y=[])

        self.source_data = ColumnDataSource(data=source_data_formated)

        self._BOKEH_EPSG = "3857"

        self._X_RANGE_DEFAULT = (-200000, 600000)
        self._Y_RANGE_DEFAULT = (-100000, 700000)

    def run(self):
        self._bokeh_widgets()
        self._bokeh_map_init()
        self._bokeh_layers_init()
        self._bokeh_map_layout()


    def _bokeh_map_init(self):

        # set canvas
        self._plot = figure(
            title="USGS EarthQuakes !",
            plot_width=800,
            plot_height=600,
            x_range=self._X_RANGE_DEFAULT,
            y_range=self._Y_RANGE_DEFAULT,
            x_axis_type="mercator",
            y_axis_type="mercator",
            output_backend="webgl",
            tools=self._TOOLS
        )

        # set background map
        self._plot.add_tile(STAMEN_TERRAIN_RETINA)


    def _bokeh_map_layout(self):
        layout = column(
            row(self._plot),
            # row(self._geom_input_wkt, self._from_epsg_value),
            # row(widgetbox(self._grid_type)),
            # row(self._res_x_value, self._res_y_value),
            # row(self._slider_rotation),
            # row(widgetbox(self._exporting, self._to_epsg_value))
        )

        curdoc().add_root(layout)
        curdoc().title = "Map_test"


    def _bokeh_layers_init(self):

        self._plot.circle(
            x='x',
            y='y',
            source=self.source_data,
            size=2,
            color={'field': 'mag', 'transform': color_mapper},
            alpha=1,
            legend="earthquake"
        )
        label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
        self._plot.add_layout(label)


    def _bokeh_widgets(self):

        self._display_year_widget = TextInput(value="500", title="year")
        self._display_year_widget.on_change('value', self.__pull_data_from_year)

    def __pull_data_from_year(self, attrname, old, new):
        data = ImportUsgsEarthquakeData(
            self._display_year_widget,
            self._display_year_widget + 1
        ).run()

        self.source_data.data = dict(
            mag=data['mag'].tolist(),
            place=data['place'].tolist(),
            url=data['url'].tolist(),
            magType=data['magType'].tolist(),
            type=data['type'].tolist(),
            title=data['title'].tolist(),
            x=data['x'].tolist(),
            y=data['y'].tolist()
        )


