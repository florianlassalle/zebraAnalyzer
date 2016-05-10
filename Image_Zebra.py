#!coding:utf-8

import numpy as np
import cv2
import os
from process_functions import *
import time

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
		self.fish_type = ""
		self.contour = None
		self.ellipse = None
		self.hull = None
		self.area = None
		self.len_head_tail = None
		self.courbure = None
		self.head = None
		self.tail = None
		
	def write_mesures(self):
		fic = open ('../Analyze_results/resultTable.csv', "a")
		fic.write(self.name)
		fic.write(',')
		fic.write(str(self.courbure))
		fic.write(',')
		fic.write(str(self.area))
		fic.write(',')
		fic.write(str(self.len_head_tail))
		fic.write ('\n')

	def process(self):
		self.img = gaussianBlur(self.img)
		self.img = threshold(self.img,self.treshold_value)
		self.img = fill_holes(self.img)
		# select the contour of the biggest binary object
		contour,hierarchy = cv2.findContours(self.img.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		self.contour = contour[find_bigest(contour,hierarchy)]
		self.ellipse = cv2.fitEllipse(self.contour)
		self.area = cv2.contourArea(self.contour)
		# compute the convex hull
		self.hull = cv2.convexHull(self.contour)
		#detect the fish's type
		self.fish_type = detect_type(self.ellipse)
		#draw the back of the fish
		self.cop, self.courbure,self.head,self.tail,self.len_head_tail = draw_backContour(self.hull,self.cop,self.contour,self.fish_type)
		# detection of the yolk
		self.cop = detect_yolk_launcher(self.cop.copy(),self.cop,self.fish_type)
		#write the name on the image
		cv2.putText(self.cop,self.name,(10,self.cop.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 2,(255,255,255),2,cv2.CV_AA)
		# save analyse's results
		self.write_mesures()
		#cv2.imshow(self.name,self.cop)
		cv2.imwrite(str("../Analyze_results/Images/"+self.name+".jpg"),self.cop)



def create_result_file():
	fic = open ('../Analyze_results/resultTable.csv', "w")
	fic.write('image_name')
	fic.write(',')
	fic.write('dorsal_circularity')
	fic.write(',')
	fic.write('fish_area')
	fic.write(',')
	fic.write('fish_length')
	fic.write('\n')
	

def process_all_images(directory):
	imagesPool = []
	os.chdir(directory)
	
	create_result_file()
	deb = time.clock()
	for element in os.listdir(directory):
		imagesPool.append(Image_zebra(element))
	
	""" applying algorithms on each image in the previous list """ 	
	for pic in imagesPool:
		pic.process()
	end = time.clock()
	print "time : ", end - deb


		
