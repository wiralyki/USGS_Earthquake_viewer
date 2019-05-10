# display USA earthquakes

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
from bokeh.models import BoxSelectTool


class ShakeMeToBokeh:

    _TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    def __init__(self):

        source_data_formated = dict(mag=[], place=[], year=[], url=[], magType=[], type=[], title=[], x=[], y=[])
        self.source_data = ColumnDataSource(data=source_data_formated)

        self._X_RANGE_DEFAULT = (-800000, 1200000)
        self._Y_RANGE_DEFAULT = (-400000, 1400000)

    def run(self):
        self._symbology()
        self._bokeh_widgets()
        self._bokeh_map_init()
        self._bokeh_layers_init()
        self._bokeh_map_layout()


    def _bokeh_map_init(self):
        hover = HoverTool(tooltips=[
            ("nom", "@title"),
            ("Lieu", "@place"),
            ("Annee", "@year"),
            ("magnitude", "@mag"),
            # ("impact", "@detail")
        ])

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
            tools=[hover, self._TOOLS]
        )

        # set background map
        self._plot.add_tile(STAMEN_TERRAIN_RETINA)


    def _bokeh_map_layout(self):
        layout = column(
            row(self._plot),
            # row(self._geom_input_wkt, self._from_epsg_value),
            row(self._display_year_widget),
            # row(self._res_x_value, self._res_y_value),
            row(self._slider),
            # row(widgetbox(self._exporting, self._to_epsg_value))
        )

        curdoc().add_root(layout)
        curdoc().title = "Map_test"


    def _bokeh_layers_init(self):

        self._plot.circle(
            x='x',
            y='y',
            source=self.source_data,
            size='mag',
            color={'field': 'mag', 'transform': self._color_mapper},
            alpha=1,
            legend="earthquake"
        )


    def _bokeh_widgets(self):

        self._display_year_widget = TextInput(value="1950", title="Année")
        self._display_year_widget.on_change('value', self.__pull_data_from_year)

        self._slider = Slider(start=1950, end=2019, value=1950, step=1, title="Année")
        self._slider.on_change('value', self._slider_update)

    def __pull_data_from_year(self, attrname, old, new):
        data = ImportUsgsEarthquakeData(
            int(self._display_year_widget.value),
            int(self._display_year_widget.value) + 1
        ).run()
        print(len(data))
        self.source_data.data = dict(
            mag=data['mag'].tolist(),
            place=data['place'].tolist(),
            url=data['url'].tolist(),
            year=data['year'].tolist(),
            magType=data['magType'].tolist(),
            type=data['type'].tolist(),
            title=data['title'].tolist(),
            x=data['x'].tolist(),
            y=data['y'].tolist()
        )

    def _slider_update(self, attrname, old, new):
        data = ImportUsgsEarthquakeData(
            int(self._slider.value),
            int(self._slider.value) + 1
        ).run()
        print(len(data))
        # label.text = self._display_year_widget.value
        self.source_data.data = dict(
            mag=data['mag'].tolist(),
            place=data['place'].tolist(),
            url=data['url'].tolist(),
            year=data['year'].tolist(),
            magType=data['magType'].tolist(),
            type=data['type'].tolist(),
            title=data['title'].tolist(),
            x=data['x'].tolist(),
            y=data['y'].tolist()
        )



    def _symbology(self):
        self._color_mapper = LinearColorMapper(
            palette='Magma256',
            low=1,
            high=10
        )


ShakeMeToBokeh().run()