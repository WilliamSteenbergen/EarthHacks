import pandas as pd
import geopandas as gpd
from planet import api
from planet.api import filters
from datetime import datetime
import json
import Prediction.helperFunctions as HF
import ee
import time
import requests
import os
import json
from requests.auth import HTTPBasicAuth
import pathlib


def download_results(results, overwrite=False):
	results_urls = [r['location'] for r in results]
	results_names = [r['name'] for r in results]
	print('{} items to download'.format(len(results_urls)))

	for url, name in zip(results_urls, results_names):
		path = pathlib.Path(os.path.join('data', name))

		if overwrite or not path.exists():
			print('downloading {} to {}'.format(name, path))
			r = requests.get(url, allow_redirects=True)
			path.parent.mkdir(parents=True, exist_ok=True)
			open(path, 'wb').write(r.content)
		else:
			print('{} already exists, skipping {}'.format(path, name))


if __name__ == '__main__':
	ordersUrl = 'https://api.planet.com/compute/ops/orders/v2/3baa3345-c124-413b-a6f9-1d5053751da4'
	auth = HTTPBasicAuth("e262ca6835e64fa7b6975c558237e509", '')

	r = requests.get(ordersUrl, auth=auth)
	response = r.json()
	results = response['_links']['results']

	download_results(results)

	ordersUrl = 'https://api.planet.com/compute/ops/orders/v2/84cb4b0c-25f2-4fa8-b3c6-c92d4bce897a'
	auth = HTTPBasicAuth("e262ca6835e64fa7b6975c558237e509", '')

	r = requests.get(ordersUrl, auth=auth)
	response = r.json()
	results = response['_links']['results']

	download_results(results)