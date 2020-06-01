import webbrowser
import folium
import geehydro
import datetime as dt
from IPython.display import Image
import pandas as pd
import numpy as np
from datetime import datetime
import json
import requests
import geopandas as gpd
from owslib.wms import WebMapService
import matplotlib.pyplot as plt
import shapely
import time
import os
import math
import Prediction.helperFunctions as HF
import ee


#ee.Authenticate() #should take you to Google SSO page --- use Stanford credentials!
ee.Initialize()

def loadData(dir):
	frames = []
	for year in range(2018, 2016, -1):
		frames.append(gpd.read_file(dir + str(year) + '_perimeters_dd83.shp'))

	all_fires = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True) )
	return all_fires

def save(fireData, i):
	# testing the bounding box approach (fire should be in Paradise Area).... will later loop through i....
	distance = 45

	# Initialize landsat as all Landsat 8 Surface Reflectance Tier 1 filtered for the three months preceding the fire
	landsat = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
	landsatPre = landsat.filterDate(HF.getDatePre(fireData, i)[0], HF.getDatePre(fireData, i)[1])
	landsatPost = landsat.filterDate(HF.getDatePost(fireData, i)[0], HF.getDatePost(fireData, i)[1])

	# Set an AOI (Area of Interest)
	LAWarmbox = HF.getbox(i, distance, fireData)
	LAWarm_AOI = ee.Geometry.Rectangle([LAWarmbox[0], LAWarmbox[1],
	                                    LAWarmbox[2], LAWarmbox[3]])

	# call the GeoJSON
	landsatPre_AOI = landsatPre.filterBounds(LAWarm_AOI)
	landsatPost_AOI = landsatPost.filterBounds(LAWarm_AOI)

	# Check on the number of images and bands available in the time of interest
	# print('Total number:', landsat_AOI.size().getInfo())
	# print(landsat_AOI.first().bandNames().getInfo())

	# MODIS is fire perimeter re-defined as an image from GEE dataset
	MODIS = ee.ImageCollection("MODIS/006/MCD64A1").filter(
		ee.Filter.date(HF.getDatePre(fireData, i)[0], HF.getDatePost(fireData, i)[1]))
	burnedArea = MODIS.select('BurnDate')
	palette = ['pink']
	burnedArea_parameters = {'min': 0,
	                         'max': 1,
	                         'dimensions': 512,
	                         'palette': palette,
	                         'region': LAWarm_AOI}
	# my_map.addLayer(burnedArea, burnedArea_parameters)
	# my_map

	# TIGER data set goes and gets census tracks and makes any with >30 Yellow, Orange, and Red...
	dataset = ee.FeatureCollection('TIGER/2010/Blocks')
	palette = ['black', 'yellow', 'orange', 'red']
	opacity = 0.7
	visParams = {
		'min': 30.0,
		'max': 100.0,
		'palette': palette,
		'opacity': opacity,
		'region': LAWarm_AOI}
	# Turn the strings into numbers
	popImage = ee.Image().float().paint(dataset, 'pop10')
	# my_map.addLayer(popImage, visParams, 'TIGER')
	# my_map

	# get least cloud of the RGB/Infrared LANDSAT image
	least_cloudyPre = ee.Algorithms.Landsat.simpleComposite(landsatPre_AOI, 75, 3)
	least_cloudyPost = ee.Algorithms.Landsat.simpleComposite(landsatPost_AOI, 75, 3)

	# least_cloudyPre = ee.Image(landsatPre_AOI.sort('CLOUD_COVER').first())
	# least_cloudyPost = ee.Image(landsatPost_AOI.sort('CLOUD_COVER').first())


	# get MODIS burn image into right format
	burnedImage = burnedArea.reduce(ee.Reducer.mean())

	# refrence population image from TIGER as above
	popImage = popImage

	# get socioeconomic data image in same route
	# PLACEHOLDER

	# convert AOI bounding box to region foormat consistent with get_url function
	myregion = HF.get_region(LAWarm_AOI)

	LAWARM_vis_bandPre = least_cloudyPre.select(['B5', 'B4', 'B3', 'B2'])
	LAWARM_vis_bandPost = least_cloudyPost.select(['B5', 'B4', 'B3', 'B2'])

	HF.save("LandSatPre", LAWARM_vis_bandPre, 30, myregion, i)
	HF.save("LandSatPost", LAWARM_vis_bandPost, 30, myregion, i)
	HF.save("Population", popImage, 30, myregion, i)   # NOTE: likely want it to be >30....
	HF.save("Burn", burnedImage, 30, myregion, i)
	# url_Socio = get_url("Socio", TBD, 10, myregion)

	return

if __name__ == '__main__':
	dir = '/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/data/'
	data = loadData(dir)
	CalData = gpd.GeoDataFrame(data[data.state=='CA'])
	CalDataUnique = CalData.drop_duplicates(subset='incidentna',keep="first")

	for i in range(0, len(CalDataUnique)):
		save(CalDataUnique, i)




