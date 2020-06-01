import math
import webbrowser
import datetime as dt
import shapely
import numpy as np
import ee





# degrees to radians
def deg2rad(degrees):
    return math.pi*degrees/180.0
# radians to degrees
def rad2deg(radians):
    return 180.0*radians/math.pi

# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

def boundingBox(longitudeInDegrees, latitudeInDegrees, halfSideInKm):
    lon = deg2rad(longitudeInDegrees)
    lat = deg2rad(latitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    min_lat = lat - halfSide/radius
    max_lat = lat + halfSide/radius
    min_lon = lon - halfSide/pradius
    max_lon = lon + halfSide/pradius
    Bbox = (rad2deg(min_lon), rad2deg(min_lat), rad2deg(max_lon), rad2deg(max_lat))
    return Bbox

def save(name, imageFile, scale, region, i):
    """It will open and download automatically a zip folder containing Geotiff data of 'image'.
    If additional parameters are needed, see also:
    https://github.com/google/earthengine-api/blob/master/python/ee/image.py

    Parameters:
        name (str): name of the created folder
        image (ee.image.Image): image to export
        scale (int): resolution of export in meters (e.g: 30 for Landsat)
        region (list): region of interest

    Returns:
        path (str)
     """

    task_config = {
	    'fileFormat': 'GeoTIFF',
	    'scale': scale,
	    'region': region,
	    'folder': 'TestComposite'
    }

    task = ee.batch.Export.image.toDrive(imageFile, str(i) + name, **task_config)
    task.start()
    print('done')

def get_region(geom):
    """Get the region of a given geometry, needed for exporting tasks.

    Parameters:
        geom (ee.Geometry, ee.Feature, ee.Image): region of interest

    Returns:
        region (list)
    """
    if isinstance(geom, ee.Geometry):
        region = geom.getInfo()["coordinates"]
    elif isinstance(geom, ee.Feature, ee.Image):
        region = geom.geometry().getInfo()["coordinates"]
    elif isinstance(geom, list):
        condition = all([isinstance(item) == list for item in geom])
        if condition:
            region = geom
    return region

#find the dates for the after photo --- currently set to 20 days later...
def getDatePost(fire_perims, i):
    #get date and turn it into date time...
    date = fire_perims['perimeterd'].iloc[i]
    firedate = dt.datetime.strptime(date, '%Y-%m-%d')
    firedate_str = firedate.strftime("%Y-%m-%d")
    interval_enddate = firedate + dt.timedelta(days = 20)
    interval_enddate_str = interval_enddate.strftime("%Y-%m-%d")
    return (firedate_str,interval_enddate_str)

#find the dates for the before photo...
def getDatePre(fire_perims, i):
    #get date and turn it into date time...
    date = fire_perims['perimeterd'].iloc[i]
    firedate = dt.datetime.strptime(date, '%Y-%m-%d')
    interval_startdate = firedate - dt.timedelta(days = 100)
    firedate_str=interval_startdate.strftime("%Y-%m-%d")
    interval_enddate= firedate - dt.timedelta(days = 20)
    interval_enddate_str=interval_enddate.strftime("%Y-%m-%d")
    return (firedate_str,interval_enddate_str)

def getbox(i, distance, all_fires):
    if type(all_fires['geometry'].iloc[i]) == shapely.geometry.polygon.Polygon:
        test_polygon = all_fires['geometry'].iloc[i]
        ade_center = np.array(test_polygon.representative_point())
        polybbox = boundingBox(ade_center[0], ade_center[1], distance)
    elif type(all_fires['geometry'].iloc[i]) == shapely.geometry.multipolygon.MultiPolygon:
        test_polygon = all_fires['geometry'].iloc[i][0]
        ade_center = np.array(test_polygon.representative_point())
        polybbox = boundingBox(ade_center[0], ade_center[1], distance)
    return polybbox