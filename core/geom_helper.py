from shapely.wkt import loads
from shapely.ops import transform
import pyproj
from functools import partial


def ogr_reprojection(geometry, from_epsg, to_epsg):
    """
    ogr_reprojection

    :type geometry: shapely.geometry.*
    :type from_epsg: int
    :type to_epsg: int
    :rtype: shapely.geometry.*
    """

    geom_reprojected = transform(
        partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(init='EPSG:3857')), geometry)

    return geom_reprojected