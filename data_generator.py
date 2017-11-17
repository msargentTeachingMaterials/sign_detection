import cv2
import numpy as np 
import os
import shutil
import multiscale_detect as md
import json
import itertools
from random import randint
from scipy import ndimage


#returns a dictionary of imagepaths -> array of bounding boxes 
def getBoundingBoxesForImages(jsonString):
	boxes = {}
	jsonData = json.loads(jsonString)
	result = {x["filename"]: annotationsToTuples(x["annotations"]) for x in jsonData}
	return result

#convenience method to convert an array of annotation dicts found  in the json file
#to tuples of coordinates for a bounding rectangle, (x1, y1, x2, y2)
def annotationsToTuples(annotationArray):
	result = [(a['x'], a['y'], a["width"], a["height"]) for a in annotationArray]
	return result

#gets a list of sign images from scenes containing signs and json file of labels
def getImagesFromJSON(jsonString, imgdir=os.getcwd()):
	signs = []
	boxes = getBoundingBoxesForImages(jsonString)
	for key, arr in boxes.items():
		scene = cv2.imread(imgdir + "/" + key)
		if scene is None:
			continue
		for coord in arr:
			x, y, width, height = int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3]) 
			if width < 40 or height < 40: 
				continue			
			img = scene[y:y+height, x: x+width, :]
			signs.append(img)
	return signs


def getHeightsWidths(jsonString):
	jsonData = json.loads(jsonString)
	result =  [[(a["width"], a["height"]) for a in elem["annotations"]] for elem in jsonData]
	result = [item for sublist in result for item in sublist]
	return result

def getAllFiles(sourceDirectory):
	files = list(filter( lambda f: not f.startswith('.'), os.listdir(sourceDirectory)))
	return files


def getRandomFile(sourceDirectory):
	files = getAllFiles(sourceDirectory)
	#select random file
	n = len(files) - 1
	fileno = randint(0, n)
	filename = files[fileno]
	return filename

def getRandomImage(sourceDirectory):
	filename = getRandomFile(sourceDirectory)

	img = cv2.imread(sourceDirectory + "/" + filename, -1)
	if img is None:
		print (filename, "is not an image")
		return
	else:
		return filename, img

def getRandomMultiple(directory, num, label):
	data = []
	for i in range(num):
		filename, img = getRandomImage(directory)
		#tuple with filename, image, and label
		data.append((directory + "/" + filename, img, label))	
		cv2.imwrite(directory + "/" + filename, img)
	return data

def cropToRatio(img, ratio):
	if ratio > 1:
		h = img.shape[0]
		w = int(round(h / ratio))
	else:
		w = img.shape[1] 
		h = int(round(w * ratio))

	return img[:h, :w, :]


def get_mods(img):    
    results = []
    results.extend([ndimage.rotate(img, 2), ndimage.rotate(img, -2), cv2.flip(img, 1)])
    return results


#need to get HOGs for different aspect ratios
def ratiosToHOGS(ratios, minDim):
    blockSize = (16,16)
    blockStride = (8,8)
    cellSize = (8,8)
    nbins = 9
    derivAperture = 1
    winSigma = -1
    histogramNormType = 0
    L2HysThreshold = 2.0000000000000001e-01
    gammaCorrection = 0
    nlevels = 64
    HOGs = []
    dims = []
    
    if minDim % 8 != 0:
        raise("minDim not divisible by 8", minDim)
    
    for r in ratios:
        prod = int(r * minDim)
        dimW = prod - (prod % 8)       
        dimens = (minDim, dimW)
        hog = cv2.HOGDescriptor(dimens,blockSize,blockStride,cellSize,nbins,derivAperture,winSigma,
                        histogramNormType,L2HysThreshold,gammaCorrection,nlevels)
        HOGs.append(hog)
        dims.append((minDim, dimW))
    return HOGs, dims



if __name__ == "__main__":
	image = cv2.imread("blanks/0.png")
	img = cropToRatio(image, 1.2)


	# #set parameters for hog
	# winSize = (80,80)
	# blockSize = (16,16)
	# blockStride = (8,8)
	# cellSize = (8,8)
	# nbins = 9
	# derivAperture = 1
	# winSigma = -1
	# histogramNormType = 0
	# L2HysThreshold = 2.0000000000000001e-01
	# gammaCorrection = 0
	# nlevels = 64
	# hog = cv2.HOGDescriptor(winSize,blockSize,blockStride,cellSize,nbins,derivAperture,winSigma,
	#                         histogramNormType,L2HysThreshold,gammaCorrection,nlevels)




	
	