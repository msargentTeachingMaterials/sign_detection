import imutils 
import numpy as np
from collections import namedtuple
import cv2

'''
Code in this module is mostly courtesy of Adrian Rosebrock. 
See http://www.pyimagesearch.com/2015/03/16/image-pyramids-with-python-and-opencv/
http://www.pyimagesearch.com/2015/03/23/sliding-windows-for-object-detection-with-python-and-opencv/
http://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
'''

def pyramid(image, scale=1.5, minSize=(30, 30)):
	yield image

	while True:
		w = int(image.shape[1] / scale)
		image = imutils.resize(image, width=w)

		if image.shape[0] < minSize[1] or image.shape[1] < min([0]):
			break

		yield image


def sliding_window(image, stepSize, windowSize=(80,80)):
	# slide a window across the image
	for y in xrange(0, image.shape[0], stepSize):
		for x in xrange(0, image.shape[1], stepSize):
			# yield the current window
			yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])


 
# Malisiewicz et al.
def non_max_suppression_fast(boxes, overlapThresh):
	# if there are no boxes, return an empty list
	if len(boxes) == 0:
		return []
 
	# if the bounding boxes integers, convert them to floats --
	# this is important since we'll be doing a bunch of divisions
	if boxes.dtype.kind == "i":
		boxes = boxes.astype("float")
 
	# initialize the list of picked indexes	
	pick = []
 
	# grab the coordinates of the bounding boxes
	x1 = boxes[:,0]
	y1 = boxes[:,1]
	x2 = boxes[:,2]
	y2 = boxes[:,3]
 
	# compute the area of the bounding boxes and sort the bounding
	# boxes by the bottom-right y-coordinate of the bounding box
	area = (x2 - x1 + 1) * (y2 - y1 + 1)
	idxs = np.argsort(y2)
 
	# keep looping while some indexes still remain in the indexes
	# list
	while len(idxs) > 0:
		# grab the last index in the indexes list and add the
		# index value to the list of picked indexes
		last = len(idxs) - 1
		i = idxs[last]
		pick.append(i)
 
		# find the largest (x, y) coordinates for the start of
		# the bounding box and the smallest (x, y) coordinates
		# for the end of the bounding box
		xx1 = np.maximum(x1[i], x1[idxs[:last]])
		yy1 = np.maximum(y1[i], y1[idxs[:last]])
		xx2 = np.minimum(x2[i], x2[idxs[:last]])
		yy2 = np.minimum(y2[i], y2[idxs[:last]])
 
		# compute the width and height of the bounding box
		w = np.maximum(0, xx2 - xx1 + 1)
		h = np.maximum(0, yy2 - yy1 + 1)
 
		# compute the ratio of overlap
		overlap = (w * h) / area[idxs[:last]]
 
		# delete all indexes from the index list that have
		idxs = np.delete(idxs, np.concatenate(([last],
			np.where(overlap > overlapThresh)[0])))
 
	# return only the bounding boxes that were picked using the
	# integer data type
	return boxes[pick].astype("int")


# Code for intersection over union; taken from http://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/

def bb_intersection_over_union(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	#For non overlapping rectangles
	if interArea < 0:
		interArea = 0

	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	unionArea = float(boxAArea + boxBArea - interArea)
	iou = interArea / unionArea

	# return the intersection over union value
	return iou

'''
IoU not useful for my project, where the window must contain the entire ground truth box. Defining
my own function that measures 1) whether gt is contianed, and 2) how large gt is compared to window
Coordinates in parameter boxes in following order: min x, min y, max x, max y
'''
def containsWithFit(window, gtBox):
	#check if window contains gtBox

	if not(window[0] < gtBox[0] and window[1] < gtBox[1] and window[2] > gtBox[2] and window[3] > gtBox[3]):
		return 0
		
	windowArea = (window[2]-window[0]+.1)*(window[3]-window[1] + .1)
	gtBoxArea = (gtBox[2]-gtBox[0]+.1)*(gtBox[3]-gtBox[1] + .1)
	return gtBoxArea/windowArea




# define the list of example detections
# examples = [
# 	Detection("image_0002.jpg", [39, 63, 203, 112], [54, 66, 198, 114]),
# 	Detection("image_0016.jpg", [49, 75, 203, 125], [42, 78, 186, 126]),
# 	Detection("image_0075.jpg", [31, 69, 201, 125], [18, 63, 235, 135]),
# 	Detection("image_0090.jpg", [50, 72, 197, 121], [54, 72, 198, 120]),
# 	Detection("image_0120.jpg", [35, 51, 196, 110], [36, 60, 180, 108])]



