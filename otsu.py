import numpy as np
from osgeo import gdal
import sys

""" Use Otsu's method to caluclate optimal threshold ignoring nodata values """
nbins = 500
filename = sys.argv[1]
print("Opening {fName}".format(fName=filename))

dataset = gdal.Open(filename)
band = dataset.GetRasterBand(1)

stats = band.ComputeStatistics(False)
gain = (stats[1] - stats[0]) / nbins
half_gain = gain * 0.5

#Get histogram. Do not allow overlays! The first and last buckets must contain at least 1 to avoid divide-by-zero.
hist = np.array(band.GetHistogram(min=stats[0]-half_gain, max=stats[1]+half_gain, buckets=nbins, approx_ok=0)).astype(float) 

bin_centers = [stats[0] + i * gain for i in range(0, nbins)]

# class probabilities for all possible thresholds
weight1 = np.cumsum(hist)
weight2 = np.cumsum(hist[::-1])[::-1]
# class means for all possible thresholds
mean1 = np.cumsum(hist * bin_centers) / weight1
mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]

# Clip ends to align class 1 and class 2 variables:
# The last value of `weight1`/`mean1` should pair with zero values in
# `weight2`/`mean2`, which do not exist.
variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2

idx = np.argmax(variance12)
threshold = bin_centers[:-1][idx]

print("THRESHOLD:{thresh}".format(thresh=threshold))