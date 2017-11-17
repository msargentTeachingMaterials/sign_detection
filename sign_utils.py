import cv2
import numpy as np 
import random 
import os
import PIL
from PIL import Image, ImageFont, ImageDraw
import string
import shutil
import csv

#for individual images, helper methods
def makeRandomImage(sourceDirectory, xdim, ydim):

	_, img = getRandomImage(sourceDirectory)

	#load image, get the max x and y values I can start my selection of upper left corner from
	cydim, cxdim = img.shape[0], img.shape[1]
	if cxdim < xdim or cydim < ydim:
		factor = max(xdim/float(cxdim + 10), float(ydim/cydim+10))
		img = cv2.resize(img, (0,0), fx=factor, fy=factor)
		cydim, cxdim, _ = img.shape
	
	maxh = cydim - ydim
	maxw = cxdim - xdim

	px = random.randint(0, maxw)
	py = random.randint(0, maxh)
	img = img[py:py + ydim, px:px + xdim,:]
	return img

def embed(inner, outer):
	#embed inner into outer (center image with largest dim filling 80%, retain aspect ratio)
	inydim = inner.shape[0]
	inxdim = inner.shape[1]
	outydim = outer.shape[0]
	outxdim = outer.shape[1]

	if inydim > outydim-10 or inxdim > outxdim -10:
		print "inner image must be at least 20px smaller than outer image for both xdim and ydim"
		return

	#calculate starting point (offsets)
	diffx = outxdim - inxdim
	diffy = outydim - inydim

	x_offset = random.randint(5, diffx)
	y_offset = random.randint(5, diffy)

	#embed: check if has alpha channel (4th dim) --- need to handle that case
	if inner.shape[2] == 4:		
		#from http://stackoverflow.com/a/14102014/399741
		for c in range(0,3):
			outer[y_offset:y_offset+inydim, x_offset:x_offset+inxdim, c] = inner[:,:,c] * (inner[:,:,3]/255.0) +  outer[y_offset:y_offset+inydim, x_offset:x_offset+inxdim, c] * (1.0 - inner[:,:,3]/255.0)
		return outer	
	else:
		outer[y_offset:inydim+y_offset, x_offset: inxdim+x_offset, :3] = inner
		return outer

def getRandomFile(sourceDirectory):
	files = getAllFiles(sourceDirectory)
	#select random file
	n = len(files) - 1
	fileno = random.randint(0, n)
	filename = files[fileno]
	return filename

def getAllFiles(sourceDirectory):
	files = filter( lambda f: not f.startswith('.'), os.listdir(sourceDirectory))
	return files

def getRandomImage(sourceDirectory):
	filename = getRandomFile(sourceDirectory)

	img = cv2.imread(sourceDirectory + "/" + filename, -1)
	if img is None:
		print filename, "is not an image"
		return
	else:
		return filename, img

def generateArtificial(sourceDirectory, blankSourceDirectory, dim):
	_, img = getRandomImage(sourceDirectory)
	imgh = img.shape[0]
	imgw = img.shape[1]

	#get blank to embed in
	blank = makeRandomImage(blankSourceDirectory, dim, dim)

	factor = (dim -10.0)/max(imgh, imgw)
	ydim = int(factor*imgh)

	img = cv2.resize(img, (0, 0), fx=factor, fy=factor)		
	return embed(img, blank)

def addRoundedRectangleBorder(img):
	#Based on c++ code from http://stackoverflow.com/a/18975399/399741
	ydim, xdim, channels = img.shape

	border_radius = int(xdim * random.randint(1, 10)/100.0)
	line_thickness = int(max(xdim, ydim) * random.randint(1, 3)/100.0)
	edge_shift = int(line_thickness/2.0)

	red = random.randint(230,255)
	green = random.randint(230,255)
	blue = random.randint(230,255)
	color = (blue, green, red)

	#draw lines
	#top
	cv2.line(img, (border_radius, edge_shift), 
		(xdim - border_radius, edge_shift), (blue, green, red), line_thickness)
	#bottom
	cv2.line(img, (border_radius, ydim-line_thickness), 
		(xdim - border_radius, ydim-line_thickness), (blue, green, red), line_thickness)
	#left
	cv2.line(img, (edge_shift, border_radius), 
		(edge_shift, ydim  - border_radius), (blue, green, red), line_thickness)
	#right
	cv2.line(img, (xdim - line_thickness, border_radius), 
		(xdim - line_thickness, ydim  - border_radius), (blue, green, red), line_thickness)

	#corners
	cv2.ellipse(img, (border_radius+ edge_shift, border_radius+edge_shift), 
		(border_radius, border_radius), 180, 0, 90, color, line_thickness)
	cv2.ellipse(img, (xdim-(border_radius+line_thickness), border_radius), 
		(border_radius, border_radius), 270, 0, 90, color, line_thickness)
	cv2.ellipse(img, (xdim-(border_radius+line_thickness), ydim-(border_radius + line_thickness)), 
		(border_radius, border_radius), 10, 0, 90, color, line_thickness)
	cv2.ellipse(img, (border_radius+edge_shift, ydim-(border_radius + line_thickness)), 
		(border_radius, border_radius), 90, 0, 90, color, line_thickness)

	return img

def getRandomText(length, font, font_size):		
	text = " "
	space_length = font.getsize(" ")[0]
	chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYX0123456789     "
	while font.getsize(text)[0] < length:
		text += random.choice(chars)
	return text

def generateRandomSign(xdim, ydim):
	red = random.randint(0,10)
	green = random.randint(80, 160)
	blue = int(green * random.randint(60, 95)/100.0)
	img = np.zeros((ydim, xdim, 3), np.uint8)
	img[:] = (blue, green, red)
	img = addRoundedRectangleBorder(img)

	p_img = Image.fromarray(img) #converting to PIL format to draw text
	draw = ImageDraw.Draw(p_img)
	no_lines = random.randint(1, 5) if ydim > 80 else 1 #Hyw guides signs
	#usually don't have more than 4 lines. If the sign is small, put only one line

	font_size = int(ydim/(no_lines + 4))
	font = ImageFont.truetype("HWYGOTH.TTF", font_size)

	for j in range(0, no_lines):		
		text = getRandomText(0.6 * xdim, font, font_size)
		right_edge = int(.1 * xdim)
		draw.text((right_edge, j * (right_edge + .5 * font_size) + 10), text, font=font)

	img = np.array(p_img)	
	
	return img

def generateGeneratedSign(blankSourceDirectory, xdim, ydim):
	innerydim = int(max(.5, random.random()) * (xdim -10))
	img = generateRandomSign(xdim-10, innerydim)
	blank = makeRandomImage(blankSourceDirectory, xdim, ydim)
	return embed(img, blank)


#dataset

def getMultiple(directory, num, label):
	data = []
	for i in range(num):
		filename, img = getRandomImage(directory)
		#tuple with filename, image, and label
		data.append((directory + "/" + filename, img, label))	
		cv2.imwrite(directory + "/" + filename, img)
	return data

def genNegatives(fromDir, toDir, num, xdim, ydim):
	data = []
	for i in range(num):
		img = makeRandomImage(fromDir, xdim, ydim)
		#tuple with filename, image, and label
		filename = toDir + "/" + str(i) + ".png"
		data.append((filename, img, 0))
		cv2.imwrite(filename, img)		
	return data

def genArtificial(fromDir, toDir, blankSourceDirectory, num, xdim, ydim):
	data = []
	for i in range(num):
		img = generateArtificial(fromDir, blankSourceDirectory, xdim)
		#tuple with filename, image, and label
		filename = toDir + "/" + str(i) + ".png"
		data.append((filename, img, 1))
		cv2.imwrite(filename, img)		
	return data		


def genGenerated(fromDir, toDir, num, xdim, ydim):
	data = []
	for i in range(num):
		img = generateGeneratedSign(fromDir, xdim, ydim)
		#tuple with filename, image, and label
		filename = toDir + "/" + str(i) + ".png"
		data.append((filename, img, 1))
		cv2.imwrite(filename, img)		
	return data		

def genGeneratedNoDataFile(fromDir, toDir, num, xdim, ydim):
	data = []
	for i in range(num):
		img = generateGeneratedSign(fromDir, xdim, ydim)
		#tuple with filename, image, and label
		filename = toDir + "/" + str(i) + ".png"
		cv2.imwrite(filename, img)		
	return data	


#get info from already existing images where info is stored in data file
def readDataSet():
	data = []
	with open("data.csv") as data_file:
		data_file = csv.reader(data_file)
		for row in data_file:
			img = cv2.imread(row[0])
			data.append([row[0], img, row[1]])
	return data

#verify folder is all images
def verify(folder_name):
	folder = os.listdir(folder_name)
	for file in folder:
		img = cv2.imread(folder_name + "/" + file, -1)
	if img is None:
		print file, "is not an image"


#cleanup
def emptyFolder(folder_name):
	folder = os.listdir(folder_name)

	for file in folder:
		path = os.path.abspath(folder_name +"/"+file)
		if file is not None and os.path.isfile(path):
			os.remove(path)
		else: 
			print path + " not found"


def main():
	# Guide_Sign_Image.remove_generated()
	# Guide_Sign_Image.generate_dataset(2000, 200, 200, 80)
	pass



if __name__ == "__main__":
	pass
			

	

	
	


