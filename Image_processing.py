#!coding:utf-8

import numpy as np
import cv2
import os
from process_functions import *


#### CLASS FOR IMAGE PROCESSING #####

class Image_zebra:
	def __init__(self,name):
		""" constructor:
		save the name of the image file,
		the original image and a copy to work on, all the atributes"""
		self.img = cv2.imread(name,0)
		self.cop = self.img.copy()
		self.cop = cv2.cvtColor(self.cop,cv2.COLOR_GRAY2BGR)
		self.name = name
		self.hist = cv2.calcHist([self.img],[0],None,[256],[0,256])
		self.treshold_value = triangle(self.hist)
		self.contour = None
		self.hull = None
		self.area = None
		self.len_head_tail = None
		self.courbure = None
		
	def write_mesures(self,donnee,nom):
		fic = open ('../Analyze_results/resultTable.csv', "a")
		fic.write(nom)
		fic.write(',')
		fic.write(str(donnee))
		fic.write ('\n')

	def process(self):
		self.img = gaussianBlur(self.img)
		self.img = treshold(self.img,self.treshold_value)
		self.img = fill_holes(self.img)

		# select the contour of the biggest binary object
		contour,hierarchy = cv2.findContours(self.img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		self.contour = contour[find_bigest(contour,hierarchy)]

		# compute the convex hull
		self.hull = cv2.convexHull(self.contour)

		self.cop = draw_line(self.hull,self.cop)

		# save analyse's results
		self.write_mesures(self.courbure,self.name)
		#cv2.imshow(self.name,self.cop)
		cv2.imwrite("../Analyze_results/Images"+self.name+".jpg",self.cop)



def create_result_file():
	fic = open ('../Analyze_results/resultTable.csv', "w")
	fic.write('image_name')
	fic.write(',')
	fic.write('dorsal_circularity')
	fic.write('\n')
	

def process_all_images(directory):
	imagesPool = []
	os.chdir(directory)
	print directory
	create_result_file()
	for element in os.listdir(directory):
		imagesPool.append(Image_zebra(element))
	
	""" applying algorithms on each image in the previous list """ 	
	for pic in imagesPool:
		pic.process()


		
