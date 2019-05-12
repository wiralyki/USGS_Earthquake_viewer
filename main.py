from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.layouts import row
from bokeh.models import HoverTool
from bokeh.models import LinearColorMapper
from bokeh.models import Slider
from bokeh.plotting import figure
from bokeh.tile_providers import STAMEN_TERRAIN_RETINA
from bokeh.models.widgets import TextInput
from core.data_helper import ImportUsgsEarthquakeData
from bokeh.models import ColumnDataSource, TableColumn, DataTable, NumberFormatter
from bokeh.models.widgets import PreText


class ShakeMeToBokeh:
    _SOURCES_FILE = 'sources.txt'
    _TOOLS = "box_select,pan,wheel_zoom,box_zoom,reset,save"

    def __init__(self):

        self._earthquakes_count = 0

        source_data_formated = dict(mag=[], place=[], year=[], url=[], magType=[], title=[], x=[], y=[])
        self.source_data = ColumnDataSource(data=source_data_formated)

        self._X_RANGE_DEFAULT = (-2000000, 6000000)
        self._Y_RANGE_DEFAULT = (-1000000, 7000000)

    def run(self):
        self._symbology()
        self._bokeh_widgets()
        self._bokeh_map_init()
        self._bokeh_layers_init()
        self._source_text_elements()
        self._bokeh_map_layout()


    def _bokeh_map_init(self):
        hover = HoverTool(tooltips=[
            ("nom", "@title"),
            ("Lieu", "@place"),
            ("Annee", "@year"),
            ("magnitude", "@mag"),
        ])

        # set canvas
        self._plot = figure(
            title="USGS EarthQuakes !",
            plot_width=1024,
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
            row(self._mag_value_widget, self._slider_widget, self._sources_text),
            row(self._data_table),
        )

        curdoc().add_root(layout)
        curdoc().title = "USGS Earthquakes Viewer"


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

        mag_format = NumberFormatter(format='0.0')
        table_columns = [
            TableColumn(field="title", title="nom"),
            TableColumn(field="place", title="Localisation"),
            TableColumn(field="year", title="Année"),
            TableColumn(field="mag", title="Magnitude", formatter=mag_format),
            TableColumn(field="url", title="Détails"),
        ]
        self._data_table = DataTable(source=self.source_data, columns=table_columns, width=1024, height=250, editable=True)

    def _bokeh_widgets(self):

        self._mag_value_widget = TextInput(value="5", title="Choisir la magnitude minimale:")
        self._mag_value_widget.on_change('value', self.__min_mag_value)

        self._slider_widget = Slider(start=1950, end=2019, value=1950, step=1, title="Barre temporelle")
        self._slider_widget.on_change('value', self.__slider_update)

    def __min_mag_value(self, attrname, old, new):
        data = ImportUsgsEarthquakeData(
            int(self._slider_widget.value),
            int(self._slider_widget.value) + 1,
            self._mag_value_widget.value
        ).run()
        self._earthquakes_count = len(data)

        self.source_data.data = self.__format_source_data(data)

    def __slider_update(self, attrname, old, new):
        data = ImportUsgsEarthquakeData(
            int(self._slider_widget.value),
            int(self._slider_widget.value) + 1,
            self._mag_value_widget.value
        ).run()

        self._earthquakes_count = len(data)

        self.source_data.data = self.__format_source_data(data)

    def __format_source_data(self, source_data):
        """

        :param source_data: geopandas.geodataframe.GeoDataFrame
        :return: dict
        """
        return dict(
            mag=source_data['mag'].tolist(),
            place=source_data['place'].tolist(),
            url=source_data['url'].tolist(),
            year=source_data['year'].tolist(),
            magType=source_data['magType'].tolist(),
            title=source_data['title'].tolist(),
            x=source_data['x'].tolist(),
            y=source_data['y'].tolist()
        )

    def _symbology(self):
        self._color_mapper = LinearColorMapper(
            palette='Magma256',
            low=1,
            high=10
        )

    def _source_text_elements(self):
        self._sources_text = PreText(
            text=open(self._SOURCES_FILE, 'r').read(),
            width=500,
            height=100
        )

ShakeMeToBokeh().run()