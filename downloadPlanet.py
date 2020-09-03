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
		path = '/datadrive'
		path = path + name
		r = requests.get(url, allow_redirects=True)
		open(path, 'wb').write(r.content)

		# if overwrite or not path.exists():
		# 	print('downloading {} to {}'.format(name, path))
		#
		# 	path.parent.mkdir(parents=True, exist_ok=True)
		#
		# else:
		# 	print('{} already exists, skipping {}'.format(path, name))


if __name__ == '__main__':
	urls = ['https://api.planet.com/compute/ops/orders/v2/2b5eb334-f456-410f-963b-190790e324df',
	        'https://api.planet.com/compute/ops/orders/v2/02b605e7-7715-4d38-8a68-9ac9b514c379',
	        'https://api.planet.com/compute/ops/orders/v2/ceedd5d0-cd28-4e02-a8b3-a8a34f77c8f0',
	        'https://api.planet.com/compute/ops/orders/v2/999dd5b1-9193-4401-a4ed-26c97a63b596',
	        'https://api.planet.com/compute/ops/orders/v2/2e0bf1fb-ba6f-436e-b468-259fb9f16b4c'
	]
	for ordersUrl in urls:
		auth = HTTPBasicAuth("e262ca6835e64fa7b6975c558237e509", '')

		r = requests.get(ordersUrl, auth=auth)
		response = r.json()
		results = response['_links']['results']

		download_results(results)

