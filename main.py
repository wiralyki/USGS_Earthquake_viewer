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

START_DATE = 1950
END_DATE = 2018
URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s"

dates_to_requests = get_month_start_end_date_from_period(START_DATE, END_DATE)


output_earthquakes_gdfs = []
for start_date, end_date in dates_to_requests:

    url = URL % (start_date, end_date)
    output_data = RequestsData([url]).run()

    if 'features' in output_data:

        try:
            earthquake_gdf = gdf.GeoDataFrame.from_features(
                output_data['features']
            )
        except:
            output_data_features = fix_coords_point(output_data['features'])
            earthquake_gdf = gdf.GeoDataFrame.from_features(
                output_data_features
            )

        earthquake_gdf.crs = {'init': 'epsg:4326'}
        earthquake_gdf['year'] = int(start_date.year)
        earthquake_gdf['month'] = int(start_date.month)
        earthquake_gdf = earthquake_gdf[['geometry', 'mag', 'type', 'year', 'month']]
        earthquake_gdf.to_csv('output.csv')

        output_earthquakes_gdfs.append(
            earthquake_gdf
        )
        print '-> %s to %s proceed! (%s found)' % (start_date, end_date, len(earthquake_gdf))

    else:
        print '-> %s to %s NO DATA FOUND!' % (start_date, end_date)

output_earthquakes = pd.concat(output_earthquakes_gdfs).reset_index()
output_earthquakes.to_file('earthquakes.gpkg', driver="GPKG")
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
