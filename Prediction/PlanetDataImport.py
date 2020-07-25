import pandas as pd
import geopandas as gpd
from planet import api
from planet.api import filters
from datetime import datetime
import json
import Prediction.helperFunctions as HF
import ee

#ee.Authenticate() #should take you to Google SSO page --- use Stanford credentials!
ee.Initialize()

def loadData(dir):
	frames = []
	#for year in range(2018, 2016, -1):

	frames.append(gpd.read_file(dir + str(2017) + '_perimeters_dd83.shp'))

	all_fires = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True) )
	return all_fires

def p(data):
	print(json.dumps(data, indent=2))

def getPlanetPicture(fireDataSet):
	distance = 45
	for i in range(0,100):

		client = api.ClientV1(api_key="e262ca6835e64fa7b6975c558237e509")

		geom = HF.getbox(i, distance, fireDataSet)

		geom_AOI = { "type": "Polygon", "coordinates": [geom]}


		pre_date = HF.getDatePre(fireDataSet, i)
		post_date = HF.getDatePost(fireDataSet, i)

		datePre_filter = filters.date_range('acquired', gte= pre_date[0], lte= pre_date[1])
		datePost_filter = filters.date_range('acquired', gte=post_date[0], lte=post_date[1])
		geom_filter = filters.geom_filter(geom_AOI)
		cloud_filter = filters.range_filter('cloud_cover', lte=0.03)

		andPre_filter = filters.and_filter(datePre_filter, cloud_filter, geom_filter)
		andPost_filter = filters.and_filter(datePost_filter, cloud_filter, geom_filter)

		item_types = ["PSOrthoTile"]
		reqPre = filters.build_search_request(andPre_filter, item_types)
		reqPost = filters.build_search_request(andPost_filter, item_types)

		resPre = client.quick_search(reqPre)
		resPost = client.quick_search(reqPost)

		print("it should print something :")

		for item in resPre.items_iter(1):
			print(item['id'], item['properties']['item_type'])

		for item in resPost.items_iter(1):
			print(item['id'], item['properties']['item_type'])


	imagePre = None
	imagePost = None
	return imagePre, imagePost


if __name__ == '__main__':
	dir = '/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/data/'
	data = loadData(dir)

	planetPictures = getPlanetPicture(data)


	a=1