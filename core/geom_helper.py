from shapely.wkt import loads

from osgeo import ogr
from osgeo import osr

def ogr_reprojection(geometry, from_epsg, to_epsg):
    """
    ogr_reprojection

    :type geometry: shapely.geometry.*
    :type from_epsg: int
    :type to_epsg: int
    :rtype: shapely.geometry.*
    """

    source_epsg = osr.SpatialReference()
    source_epsg.ImportFromEPSG(from_epsg)

    target_epsg = osr.SpatialReference()
    target_epsg.ImportFromEPSG(to_epsg)

    transform = osr.CoordinateTransformation(source_epsg, target_epsg)
    ogr_geom = ogr.CreateGeometryFromWkt(
        geometry.wkt
    )
    ogr_geom.Transform(transform)
    geometry = loads(ogr_geom.ExportToWkt())

    return geometry