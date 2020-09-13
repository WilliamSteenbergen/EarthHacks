import geopandas as gpd
import numpy as np
from PIL import Image
import imageio
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tifffile import imread
import os
import json
import cv2
import ee
import Prediction.helperFunctions as HF
from zipfile import ZipFile

def convertToRGB(image):
	new = np.zeros(image.shape, dtype=np.uint8)

	new[:, :, 0] = image[:, :, 2]
	new[:, :, 1] = image[:, :, 1]
	new[:, :, 2] = image[:, :, 0]
	new[:, :, 3] = image[:, :, 3]
	return new

def reshape(array, nRows, nCols):
	nRows = array.shape[0]-nRows
	nCols = array.shape[1] - nCols

	if nRows % 2 == 0 and nRows>0:
		array = array[:round(-nRows/2), :]
		array = array[round(nRows/2):, :]
	elif nRows > 0:
		array = array[:-int(np.ceil(nRows / 2)), :]
		array = array[int(np.floor(nRows / 2)):, :]

	if nCols % 2 == 0 and nCols >0:
		array = array[:, :round(-nCols/2)]
		array = array[:, round(nCols/2):]
	elif nCols > 0:
		array = array[:, :-int(np.ceil(nCols / 2))]
		array = array[:, int(np.floor(nCols / 2)):]
	return array

def filter(landsat, burn, pop, burnThres, popThres):
	filteredLandsat = copy.deepcopy(landsat)
	for band in range(0,landsat.shape[2]):
		landsat_flat = landsat[:,:,band].flatten()
		burn_flat = burn.flatten()
		pop_flat = pop.flatten()

		filterIndices = np.where((burn_flat <= burnThres) | (pop_flat <= popThres))


		landsat_flat[filterIndices] = 0
		filteredLandsat[:,:,band] = landsat_flat.reshape((landsat.shape[0],landsat.shape[1]))

	return filteredLandsat

def align(before, after):
	alignedBefore = copy.deepcopy(before)

	alignedBeforeFlattened1 = alignedBefore[:,:,0].flatten()
	alignedBeforeFlattened2 = alignedBefore[:,:,1].flatten()
	alignedBeforeFlattened3 = alignedBefore[:,:,2].flatten()
	alignedBeforeFlattened4 = alignedBefore[:, :, 3].flatten()

	afterFlat1 = after[:,:,0].flatten()
	afterFlat2 = after[:, :, 1].flatten()
	afterFlat3 = after[:, :, 2].flatten()
	afterFlat4 = after[:, :, 3].flatten()

	filter1 = afterFlat1 == 0
	filter2 = afterFlat2 == 0
	filter3 = afterFlat3 == 0
	filter4 = afterFlat4 == 0

	full_filter = filter1 & filter2 & filter3 & filter4


	alignedBeforeFlattened1[full_filter] = 0
	alignedBeforeFlattened2[full_filter] = 0
	alignedBeforeFlattened3[full_filter] = 0
	alignedBeforeFlattened4[full_filter] = 0

	flat = [alignedBeforeFlattened1, alignedBeforeFlattened2, alignedBeforeFlattened3, alignedBeforeFlattened4]

	for band in range(0, before.shape[2]):
		alignedBefore[:,:,band] = flat[band].reshape(before.shape[0], before.shape[1])

	return alignedBefore

def getSmallMatrices(matrix):
	matrices = []
	print(int(np.floor(matrix.shape[0]/50)))
	for i in range(0, 50*int(np.floor(matrix.shape[0]/50)), 50):
		for j in range(0, 50*int(np.floor(matrix.shape[1]/50)), 50):
			submatrix = matrix[i:(i+50), j:(j+50), :]

			if np.count_nonzero(submatrix)/(submatrix.shape[0]*submatrix.shape[1]*submatrix.shape[2]) > 0.8:
				matrices.append(submatrix)
	return matrices

def getLabels(before, after, images, labels):

	for smallBefore, smallAfter in zip(before, after):
		#convert to HSV
		beforeImage = matplotlib.colors.rgb_to_hsv(smallBefore[:,:,0:3])
		afterImage = matplotlib.colors.rgb_to_hsv(smallAfter[:,:,0:3])

		diff = afterImage - beforeImage
		# diff[:,:,1] = np.full((smallBefore.shape[0], smallBefore.shape[1]), max(diff[:,:,1]))
		# diff[:, :, 2] = np.full((smallBefore.shape[0], smallBefore.shape[1]), max(diff[:, :, 2]))

		label = np.count_nonzero(diff[:,:,0] > 0.2) / (smallBefore.shape[0]*smallBefore.shape[1])

		images.append(smallBefore)
		labels.append(label)

	return images, labels
#
# def loadBurn(location, datesBefore, datesAfter):
# 	MODIS = ee.ImageCollection("MODIS/006/MCD64A1").filter(
# 		ee.Filter.date(datesBefore[0], datesAfter[0]))
# 	burnedArea = MODIS.select('BurnDate')
# 	palette = ['pink']
#
# 	burnedImage = burnedArea.reduce(ee.Reducer.mean())
# 	HF.save("Burn", burnedImage, 30, myregion, i)
#
# 	return data
#
# def loadPop(location, datesBefore, datesAfter):
# 	dataset = ee.FeatureCollection('TIGER/2010/Blocks')
# 	palette = ['black', 'yellow', 'orange', 'red']
# 	opacity = 0.7
#
# 	popImage = ee.Image().float().paint(dataset, 'pop10')
# 	HF.save("Population", popImage, 30, myregion, i)  # NOTE: likely want it to be >30....
#
# 	return data

if __name__ == '__main__':
	images = []
	labels = []

	prevLocation = 0
	directory = '/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/SoloData'
	fire = -1

	for firename in os.listdir(directory):
		fire += 1
		nTif = 0
		tifNames = []

		#load zip and before and after picture
		with ZipFile(directory + '/' + firename + '/' + 'output.zip') as zip:
			for filename in zip.namelist():
				if filename[-4:] == '.tif':
					nTif += 1
					tifNames.append(filename)

			if nTif != 2: #if we didn't get before and after
				continue

			IDName = tifNames[0][18:48]

			dataBefore = zip.open(tifNames[0])
			dataBefore = Image.open(dataBefore)
			# dataBefore.show()
			dataBefore = np.array(dataBefore, np.uint8)

			dataAfter = zip.open(tifNames[1])
			dataAfter = Image.open(dataAfter)
			dataAfter = np.array(dataAfter, np.uint8)

		imageBurn = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/Final2/' + str(IDName) + 'Burn.tif'), dtype=np.uint8)
		imagePop = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/Final2/' + str(IDName) + 'Population2.tif'), dtype=np.uint8)

		# plt.imshow(imageBurn)
		# plt.show()
		#
		# plt.imshow(imagePop)
		# plt.show()

		#expand imageBurn and imagePop
		imageBurn = cv2.resize(src=imageBurn, dsize=dataAfter.shape[0:2], interpolation=cv2.INTER_CUBIC)
		imagePop = cv2.resize(src=imagePop, dsize=dataAfter.shape[0:2], interpolation=cv2.INTER_CUBIC)

		landsatAnalysisBefore = filter(dataBefore, imageBurn, imagePop, 0, 0)
		landsatAnalysisAfter = filter(dataAfter, imageBurn, imagePop, 0, 0)

		fig, axs = plt.subplots(4, 2)
		axs[0, 0].imshow(imageBurn)
		axs[0, 1].imshow(imagePop)
		axs[1, 0].imshow(dataBefore)
		axs[1, 1].imshow(dataAfter)
		axs[2, 0].imshow(landsatAnalysisBefore)
		axs[2, 1].imshow(landsatAnalysisAfter)

		# align before and after
		landsatAnalysisBefore = align(landsatAnalysisBefore, landsatAnalysisAfter)

		axs[3, 0].imshow(landsatAnalysisBefore)
		axs[3, 1].imshow(landsatAnalysisAfter)
		plt.show()

		# next step is to get smaller matrices on everything that is not zero
		smallMatricesBefore = getSmallMatrices(landsatAnalysisBefore)
		smallMatricesAfter = getSmallMatrices(landsatAnalysisAfter)

		images, labels = getLabels(smallMatricesBefore, smallMatricesAfter, images, labels)
		a = 1

	np.savez_compressed('images.npz', *images)
	np.savetxt('labels.csv', labels, delimiter=',')

	# for i in range(0, 17):
	# 	imageLandSatBefore = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Prediction/data/b2aa8218-a9ec-4d21-a53a-b47537972d93/output.zipFolder/files/PSOrthoTile/390960_1555813_2017-01-31_0e14/visual/390960_1555813_2017-01-31_0e14_RGB_Visual.tif'), dtype=np.uint8)
	# 	imageLandSatAfter = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Prediction/data/42f9f300-236b-43da-9ed6-8eef56fe3c45/output.zipFolder/files/PSOrthoTile/418140_1555514_2017-02-22_0e16/analytic/418140_1555514_2017-02-22_0e16_BGRN_Analytic.tif'), dtype=np.uint8)
	# 	imageBurn = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/Final/' + str(i) + 'Burn.tif'), dtype=np.uint8)
	# 	imagePop = np.array(imread('/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/Final/' + str(i) + 'Population.tif'),  dtype=np.uint8)
	#
	# 	# Before = convertToRGB(imageLandSatBefore)
	# 	# After = convertToRGB(imageLandSatAfter)
	# 	plt.imshow(imageLandSatBefore[:, :, 0:3])
	# 	plt.show()
	#
	# 	newRowSize = min(imageLandSatBefore.shape[0], imagePop.shape[0], imageBurn.shape[0], imageLandSatAfter.shape[0])
	# 	newColSize = min(imageLandSatBefore.shape[1], imagePop.shape[1], imageBurn.shape[1], imageLandSatAfter.shape[1])
	#
	# 	imageBurn = reshape(imageBurn, newRowSize, newColSize)
	# 	imagePop = reshape(imagePop, newRowSize, newColSize)
	# 	imageLandSatBefore = reshape(imageLandSatBefore, newRowSize, newColSize)
	# 	imageLandSatAfter = reshape(imageLandSatAfter, newRowSize, newColSize)
	#
	# 	#filteres by putting 0s on what we don't want
	# 	landsatAnalysisBefore = filter(imageLandSatBefore, imageBurn, imagePop, 0, 0)
	# 	landsatAnalysisAfter = filter(imageLandSatAfter, imageBurn, imagePop, 0, 0)
	#
	# 	fig, axs = plt.subplots(4, 2)
	# 	axs[0, 0].imshow(imageBurn)
	# 	axs[0, 1].imshow(imagePop)
	# 	axs[1, 0].imshow(imageLandSatBefore)
	# 	axs[1, 1].imshow(imageLandSatAfter)
	# 	axs[2, 0].imshow(landsatAnalysisBefore)
	# 	axs[2, 1].imshow(landsatAnalysisAfter)
	#
	# 	#align before and after
	# 	landsatAnalysisBefore = align(landsatAnalysisBefore, landsatAnalysisAfter)
	#
	# 	axs[3, 0].imshow(landsatAnalysisBefore)
	# 	axs[3, 1].imshow(landsatAnalysisAfter)
	# 	plt.show()
	#
	# 	#next step is to get smaller matrices on everything that is not zero
	# 	smallMatricesBefore = getSmallMatrices(landsatAnalysisBefore)
	# 	smallMatricesAfter = getSmallMatrices(landsatAnalysisAfter)
	#
	# 	images, labels = getLabels(smallMatricesBefore, smallMatricesAfter, images, labels)
	# 	a=1


	# np.savez_compressed('images.npz', *images)
	# np.savetxt('labels.csv', labels, delimiter=',')



