# display earthquakes

import geopandas as gdf
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
        self._IN_CRS = {'init': 'epsg:4326'}
        self._OUT_CRS = {'init': 'epsg:3857'}
        self._OUTPUT_COLUMNS = ['x', 'y', 'mag', 'type', 'year', 'month', 'description']

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

    @property
    def _mag_description(self):
        return {
            'Null': (-9999, 0.1),
            'Micro': (0.1, 2),
            'Tres mineur': (2, 3),
            'Mineur': (3, 4),
            'Leger': (4, 5),
            'Modere': (5, 6),
            'Fort': (6, 7),
            'Tres fort': (7, 8),
            'Majeur': (8, 9),
            'Devastateur': (9, 9999)
        }

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

                output_data_gdf.crs = self._IN_CRS
                output_data_gdf = output_data_gdf.to_crs(self._OUT_CRS)
                output_data_gdf['x'] = output_data_gdf.geometry.apply(lambda geom: geom.x)
                output_data_gdf['y'] = output_data_gdf.geometry.apply(lambda geom: geom.y)
                output_data_gdf['year'] = int(start_date.year)
                output_data_gdf['month'] = int(start_date.month)
                output_data_gdf.fillna(0, inplace=True)
                output_data_gdf['description'] = output_data_gdf.mag.apply(
                    lambda x: [key for key, value in self._mag_description.items() if value[0] <= x < value[1]][0]
                )
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

t1 = ImportEarthquakeData(URL, 1950, 1969)
t2 = ImportEarthquakeData(URL, 1970, 1989)
t3 = ImportEarthquakeData(URL, 1990, 1999)
t4 = ImportEarthquakeData(URL, 2000, 2009)
t5 = ImportEarthquakeData(URL, 2010, 2018)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()