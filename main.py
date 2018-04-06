# display USA earthquakes

# TODO add comments





import geojson


from shapely.geometry import shape

import geopandas as gdf
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


from core.time_helper import get_month_start_end_date_from_period
from core.requests_helper import RequestsData
import os
from threading import Thread

def fix_coords_point(features):
    for num, value in enumerate(features):

        if (not isinstance(value['geometry']['coordinates'][0], (int, float))
                or not isinstance(value['geometry']['coordinates'][1], (int, float))
        ):
            del features[num]

        elif len(value['geometry']['coordinates']) == 3:
            if not isinstance(value['geometry']['coordinates'][-1], (int, float)):
                features[num]['geometry']['coordinates'] = [
                    value['geometry']['coordinates'][0],
                    value['geometry']['coordinates'][1],
                    float(0)
                ]
    return features

class ImportEarthquakeData(Thread):

    def __init__(self, template_url, start_date, end_date, to_csv=True):
        Thread.__init__(self)
        self._CRS = {'init': 'epsg:4326'}
        self._OUTPUT_COLUMNS = ['geometry', 'mag', 'type', 'year', 'month']

        self._template_url = template_url
        self._start_date = start_date
        self._end_date = end_date
        self._to_csv = to_csv

        # output
        self._output_csv_name = 'data\earthquake_%s.csv'
        self._output_earthquakes_gdfs = []

    def run(self):
        if not self._to_csv:
            print 'Warning: Process may crash (memory limit)'

        self._get_dates_to_request()
        self._format_data()

    def _get_dates_to_request(self):

        self._dates_to_request = get_month_start_end_date_from_period(
            self._start_date,
            self._end_date
        )

    def _request_data(self, start_date, end_date):

        self._start_year = start_date.year
        url = self._template_url % (start_date, end_date)
        data_requested = RequestsData([url]).run()

        return data_requested

    def _write_data(self):

        header = False
        output_csv_file = self._output_csv_name % self._start_year
        if not os.path.isfile(output_csv_file):
            mode = 'w'
            header = True
        else:
            mode = 'a'
        self._output_data_gdf.to_csv(
            output_csv_file,
            mode=mode,
            header=header,
            index=False
        )
        self._HEADER_AND_HEADER = False

    def _format_data(self):

        for start_date, end_date in self._dates_to_request:

            data_requested = self._request_data(start_date, end_date)

            if 'features' in data_requested:

                try:
                    output_data_gdf = gdf.GeoDataFrame.from_features(
                        data_requested['features']
                    )
                except:
                    output_data_features = fix_coords_point(data_requested['features'])
                    output_data_gdf = gdf.GeoDataFrame.from_features(
                        output_data_features
                    )

                output_data_gdf.crs = self._CRS
                output_data_gdf['year'] = int(start_date.year)
                output_data_gdf['month'] = int(start_date.month)
                self._output_data_gdf = output_data_gdf[self._OUTPUT_COLUMNS]

                if self._to_csv:
                    self._write_data()
                else:
                    self._output_earthquakes_gdfs.append(
                       self._output_data_gdf
                    )
                print '-> %s to %s proceed! (%s found)' % (start_date, end_date, len(self._output_data_gdf))

            else:
                print '-> %s to %s NO DATA FOUND!' % (start_date, end_date)





START_DATE = 1950
END_DATE = 2018
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s"

# date_range = [
#     (1950, 1969)
#     # (1970, 1989)
#     # (1990, 2009)
#     # (2010, 2018)
# ]
#
# for start_date, end_date in date_range:
#     ImportEarthquakeData(URL, start_date, end_date).run()

# t1 = ImportEarthquakeData(URL, 1950, 1969)
# t2 = ImportEarthquakeData(URL, 1970, 1989)
# t3 = ImportEarthquakeData(URL, 1990, 2009)
t4 = ImportEarthquakeData(URL, 2010, 2018)

# t1.start()
# t2.start()
# t3.start()
t4.start()

# t1.join()
# t2.join()
# t3.join()
t4.join()

assert False



# # earthquake_bokeh = ColumnDataSource(data=earthquake_gdf_dict_by_year[years[0]])
# earthquake_bokeh = ColumnDataSource(data=dict(x=[], y=[], mag=[], year=[]))
#
# source = earthquake_bokeh
# # source = ColumnDataSource(pd.DataFrame(columns=['x','y','type','mag','year']))
#
#
# # display data
# TOOLS = "pan,wheel_zoom,box_zoom,reset,save"
# plot = figure(title="Shake me !", tools=TOOLS,
#            plot_width=600, plot_height=400, active_scroll = "wheel_zoom", output_backend="webgl")
#
# label = Label(x=1.1, y=18, text=str(years[0]), text_font_size='70pt', text_color='#eeeeee')
# plot.add_layout(label)
#
# plot.add_tile(STAMEN_TERRAIN_RETINA)
#
# color_mapper = LinearColorMapper(palette='Magma256', low=min(earthquake_gdf['mag']), high=max(earthquake_gdf['mag']))
# plot.circle(
#     x='x',
#     y='y',
#     source=source,
#     size=10,
#     color={'field': 'mag', 'transform': color_mapper},
#     alpha=0.5,
#     legend="earthquake"
# )
#
# # Add the slider
#
# slider = Slider(start=years[0], end=years[-1], value=years[0], step=1, title="Year")
# def slider_update(attrname, old, new):
#     year = slider.value
#     df = earthquake_gdf_dict_by_year[year]
#     label.text = str(year)
#     earthquake_bokeh.data = dict(
#         x=df['x'].tolist(),
#         y=df['y'].tolist(),
#         mag=df['mag'].tolist(),
#         year=df['year'].tolist()
#     )
# slider.on_change('value', slider_update)
#
# layout = row(plot, slider)
#
# curdoc().add_root(layout)
# curdoc().title = "Thomas est un trou du cul"
