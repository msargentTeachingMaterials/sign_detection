from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
import data_generator as dg
import json
import os
from sklearn.cluster import KMeans


def addClusterLabels(data, k=3):
	rs = [x[0]/(x[1]+1) for x in data]
	kdata = [[x,1] for x in rs]

	kmeans = KMeans(n_clusters=k).fit(kdata)
	labels = kmeans.labels_
	centroids = kmeans.cluster_centers_
	return centroids, zip(data, labels)


