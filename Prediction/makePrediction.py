import tensorflow as tf
import numpy as np
import Prediction.helperFunctions as HF
import ee
import datetime as dt
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from tifffile import imread
from Prediction.dataAnalysis import reshape




def save(image, region):

	url = image.getDownloadURL({
		'name': 'done',
		'scale': 30,
		'region': (region)
	})

	resp = urlopen(url)
	zipfile = ZipFile(BytesIO(resp.read()))

	zipfile.extractall('temp/')

	bands = [2,3,4,5]

	data = []
	for band in bands:
		data.append(np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Prediction/temp/done.B' + str(band) + '.tif'),dtype=np.uint8))

	Resultdata = np.zeros((1, 50, 50,4))
	i=0
	for band in data:
		Resultdata[0,:,:,i] = reshape(band, 50, 50)
		i += 1

	return Resultdata

def getImage(lat, lon):
	radius = 0.05

	landsat = ee.ImageCollection("LANDSAT/LC08/C01/T1_SR")
	landsat = landsat.filterDate('2010-01-01', '2020-01-01')

	AOI = ee.Geometry.Rectangle([lon - radius, lat - radius,
	                             lon + radius, lat + radius])

	landsat = landsat.filterBounds(AOI)

	least_cloudy = ee.Image(landsat.sort('CLOUD_COVER').first())


	region = HF.get_region(AOI)

	least_cloudy = least_cloudy.select(['B5', 'B4', 'B3', 'B2'])
	image = save(least_cloudy, region)

	return image


def makePrediction(lat, lon):
	ee.Initialize()
	Image = getImage(lat, lon)

	model = tf.keras.models.load_model('/Users/williamsteenbergen/PycharmProjects/EarthHacks/saved_model/Model1')
	prediction = model.predict(Image)


	return prediction[0][0]

if __name__ == '__main__':
	ee.Initialize()
	print(makePrediction(56,56))
