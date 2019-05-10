
import geopandas as gdf

import grequests
import itertools

from core.time_helper import get_month_start_end_date_from_period
from core.geom_helper import ogr_reprojection


class ImportUsgsEarthquakeData:

    _URL = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=%s&endtime=%s&minmagnitude=5"
    _FIELDS_PROPERTIES_TO_KEEP = ['mag', 'place', 'url', 'magType', 'type', 'title', 'x', 'y', 'year']

    def __init__(self, start_date, end_date, output_csv=None):

        self._IN_CRS = 4326
        self._OUT_CRS = 3857
        self._OUTPUT_COLUMNS = ['x', 'y', 'mag', 'type', 'year', 'month']

        self._start_date = start_date
        self._end_date = end_date
        self._output_csv = output_csv

        # output
        self._output_earthquakes_gdfs = []

    def run(self):
        self._get_dates_to_request()
        self._prepare_requests()
        self._query_requests()
        self._get_data()
        self._clean_data()

        return self._data

    def _get_dates_to_request(self):

        self._dates_to_request = get_month_start_end_date_from_period(
            self._start_date,
            self._end_date
        )

    def _prepare_requests(self):
        self._requests = [
            grequests.get(self._URL % (start, end))
            for start, end in self._dates_to_request
        ]

    def _query_requests(self):
        import json
        self._requests = grequests.map(self._requests)

    def _get_data(self):
        self._data = list(
            itertools.chain.from_iterable([
                query.json()['features']
                for query in self._requests
            ])
        )

    def _clean_data(self):
        #optimize field
        for idx in range(len(self._data)):
            # None value on Z...
            self._data[idx]['geometry']['coordinates'] = self._data[idx]['geometry']['coordinates'][:2]

        self._data = gdf.GeoDataFrame.from_features(self._data)
        self._data.loc[:, 'year'] = str(self._start_date)


        #pyproj bug on windows... cannot use to_crs...
        self._data['geometry'] = self._data['geometry'].apply(lambda x: ogr_reprojection(x, self._IN_CRS, self._OUT_CRS))
        self._data['x'] = self._data.geometry.x
        self._data['y'] = self._data.geometry.y

        self._data = self._data[self._FIELDS_PROPERTIES_TO_KEEP]


if __name__ == '__main__':

    START_DATE = 1950
    END_DATE = START_DATE + 1

    t1 = ImportUsgsEarthquakeData(START_DATE, END_DATE).run()
    print('aa')