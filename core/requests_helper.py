
import requests

class RequestsData(object):

    def __init__(self, urls):

        self._urls = urls

    def run(self):

        results = [
            self.retrying(url)
            for url in self._urls
        ]

        output = {}
        for data in results:
            output.update(data.json())

        return output

    def retrying(self, url):

        retrying = True
        while retrying:
            response = requests.get(url)
            if response.status_code == 200:
                retrying = False
        return response

# earthquake_gdfs = []
#
# for start_date, end_date in dates_to_requests:
#     # for data in requests_data:
#
#
#
#
#     requests_data = [f for f in requests_data][0]
#     earthquakes =  gpd.GeoDataFrame.from_features(
# #         geojson.loads(
# #             requests_data.json())
# #         )['features']
# #     )
#     earthquakes = earthquakes.loc[earthquakes.alert != None]
#     earthquakes = earthquakes[['geometry', 'mag', 'type']]
#     earthquakes['year'] = int(start_date.strftime("%Y-%m-%d").split('-')[0])
#     earthquake_gdfs.append(earthquakes.head(100))
#
# earthquake_gdf = pd.concat(earthquake_gdfs)
# earthquake_gdf.crs = {'init' :'epsg:4326'}
# earthquake_gdf = earthquake_gdf.to_crs({'init': 'epsg:3857'})
# earthquake_gdf['x'] = earthquake_gdf.geometry.apply(lambda geom: geom.x)
# earthquake_gdf['y'] = earthquake_gdf.geometry.apply(lambda geom: geom.y)
# earthquake_gdf = earthquake_gdf[['x', 'y', 'mag', 'year']]
#
# earthquake_gdf_dict_by_year = {}
# years = list(set(earthquake_gdf['year'].values))
# for year in years:
#     earthquake_gdf_dict_by_year[year] = earthquake_gdf.loc[earthquake_gdf.year == year].copy().to_dict('series')