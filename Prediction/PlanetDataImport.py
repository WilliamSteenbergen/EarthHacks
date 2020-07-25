
import geopandas as gpd

def loadData(dir):
	frames = []
	for year in range(2018, 2016, -1):
		frames.append(gpd.read_file(dir + str(year) + '_perimeters_dd83.shp'))

	all_fires = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True) )
	return all_fires

if __name__ == '__main__':
	dir = '/Users/williamsteenbergen/PycharmProjects/EarthHacks/Data/data/'
	data = loadData(dir)