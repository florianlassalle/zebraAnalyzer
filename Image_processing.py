#!coding:utf-8

import numpy as np
import cv2
import os
from math import *

##### CLASS FOR IMAGE PROCESSING #####

class Image_zebra:
	def __init__(self,name):
		""" constructor:
		save the name of the image file,
		the original image and a copy to work on."""
		self.img = cv2.imread(name,0)
		self.cop = cv2.imread(name,1)
		self.name = name
	
	def gaussianBlur(self,img):
		""" apply a blur to the image img
		impair values required for radius """
		self.img = cv2.GaussianBlur(img,(5,5),9)
	
	def treshold(self,img,tresh):
		ret,self.img = cv2.threshold(img,tresh,255,cv2.THRESH_BINARY)
	
	def fillHoles(self,img):
		""" function to fill holes in threshold images """
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(30,30))
		self.img = cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel)
		
	def showImage(self,img):
		""" function to visualize images on screen """
		cv2.imshow(self.name,img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		
	def saveImage(self):
		cv2.imwrite("./result/"+self.name,self.img)

	def triangle(self,data):
		"""
		Zack, G. W., Rogers, W. E. and Latt, S. A., 1977,
		Automatic Measurement of Sister Chromatid Exchange Frequency,
		Journal of Histochemistry and Cytochemistry 25 (7), pp. 741-753
		
		 modified from Johannes Schindelin plugin
		 """
		#find min and max
		min = 0
		dmax = 0
		max = 0
		min2 = 0
	
		for i in range(len(data)):
			if data[i]>0:
				min = i
				break
	
		if min>0 : #line to the (p==0) point, not to data[min]
			min-=1
	
		for i in range(len(data)):
			if data[i]>0:
				min2 = i
				break
	
		if min2<len(data): #line to the (p==0) point, not to data[min]
			min2 +=1
	
		for i in range(len(data)):
			if data[i] > dmax :
				max = i
				dmax = data[i]
	
		#find which is the furthest side 
		#IJ.log(""+min+" "+max+" "+min2);
		inverted = False
		if (max-min)<(min2-max):
			#reverse the histogram
			#IJ.log("Reversing histogram.");
			inverted = True
			left = 0            #index of leftmost element
			right = len(data)-1 #index of rightmost element
	
			while left < right :
				#exchange the left and right elements
				temp = data[left]
				data[left] = data[right]
				data[right] = temp
				#move the bounds toward the center
				left +=1
				right -=1
			min = len(data)-1-min2
			max = len(data)-1-max
	
		if min == max :
			#IJ.log("Triangle:  min == max.");
			return min
	
		#describe line by nx * x + ny * y - d = 0
		nx = data[max]  #   //-min; // data[min]; //  lowest value bmin = (p=0)% in the image
		ny = min - max
		d = sqrt(nx * nx + ny * ny)
		nx /= d
		ny /= d
		d = nx * min + ny * data[min]
	
		#find split point
		split = min
		splitDistance = 0
		for i in range(min+1, max,1):
			newDistance = nx * i + ny * data[i] - d
			if newDistance > splitDistance :
				split = i
				splitDistance = newDistance
	
		split -=1
	
		if inverted :
			# The histogram might be used for something else, so let's reverse it back
			left = 0
			right = len(data)-1
			while left < right :
				temp = data[left]
				data[left]  = data[right] 
				data[right] = temp
				left+=1
				right-=1
			return data.length - 1-split
		else:
			return split

	def fill_holes(self,img):
		#filling holes (je ne sait pas ce qu'il se passe)
		des = cv2.bitwise_not(img)
		contour,hier = cv2.findContours(des,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
	
		for cnt in contour:
			cv2.drawContours(des,[cnt],0,255,-1)
		#inversion des couleur
		self.img = cv2.bitwise_not(des)

	def calcul_distance(self,points,xa,xb):
		dstx = points[xa][0][0] - points[xb][0][0] # = Xa - Xb
		dsty = points[xa][0][1] - points[xb][0][1] # = Ya - Yb
		distance = sqrt(pow(dstx,2) + pow(dsty,2))
		return distance

	def calc_ellipse(self,ellipse):
		rapport = ellipse[1][0]/ellipse[1][1]
		return rapport
		
	def draw_line(self,points,img):
		# on commence par calculer la plus grande distance entre deux points successifs et on considerera que ce sont les points de la tete et de la queue.
		maxi = 0
		for i in range(len(points)-1):
			distance = self.calcul_distance(points,i,i+1)
			
			if distance > maxi :
				maxi = distance

		# dessine une ligne entre deux opints
		#on calcule d'abord la distance entre deux points successifs, et si elle est inferieure a la distance max entre 2 points successifs on trace la ligne
		longueur = 0
		for i in range(len(points)-1):
			dst = self.calcul_distance(points,i,i+1)
			
			if dst < maxi :  # = racine carree ((xa-xb) + (ya-yb))
				cv2.line(img,(points[i][0][0],points[i][0][1]),(points[i+1][0][0],points[i+1][0][1]),(0,255,0),2)
				longueur += dst

		distance = self.calcul_distance(points,0,-1)
		
		if dst < maxi:
			cv2.line(img,(points[0][0][0],points[0][0][1]),(points[-1][0][0],points[-1][0][1]),(0,255,0),2)
			longueur += dst

		rapport = self.calcul_rapport(longueur,maxi)

		return img,rapport

	def draw_back(self,points,top,bot,img):
		# pour dessine le dos du poisson
		# on commence par calculer la plus grande distance entre deux points successifs et on considerera que ce sont les points de la tete et de la queue.
		maxi = 0
		longueur = 0
		longueura =0
		longueurb = 0
		longueurc = 0
		longueurd = 0
		imga=imgb=imgc=imgd = img
		for i in range(len(points)-1):
			distance = self.calcul_distance(points,i,i+1)

			if distance > maxi :
				maxi = distance

		if top > bot:
			longueura,imga = self.drawing(points,bot,top,1,maxi,img.copy())
			top = top - len(points)
			longueurb,imgb = self.drawing(points,bot,top,-1,maxi,img.copy())


		if bot > top:
			longueurc,imgc = self.drawing(points,top,bot,1,maxi,img.copy())
			bot = bot - len(points)
			longueurd,imgd = self.drawing(points,top,bot,-1,maxi,img.copy())


		longueurs = [longueura,longueurb,longueurc,longueurd]
		images = [imga,imgb,imgc,imgd]

		long_max = 0
		for i in range(len(longueurs)):
			if longueurs[i] > long_max:
				long_max = longueurs[i]
				img = images[i]

		longueur = long_max
		tete_queue = self.calcul_distance(points,top,bot)
		rapport = self.calcul_rapport(longueur,tete_queue)

		return img,rapport

	def drawing(self,points,pt1,pt2,pas,maxi,img_dessin):
		"""
		dessine l'enveloppe entre le point pt1 et pt2, et si on rencontre maxi = le ventre, on s'arrete
		"""
		longueur = 0
		i = pt1
		while i != pt2 :
			dst = self.calcul_distance(points,i,i+1)
			
			if dst < maxi : 
				cv2.line(img_dessin,(points[i][0][0],points[i][0][1]),(points[i+1][0][0],points[i+1][0][1]),(0,255,0),2)
				longueur += dst
			else:
				return 0,None

			i += pas
		return longueur,img_dessin

	def drawEllipse(self,hull,img,elongation):
		if elongation < 0.5:
			pt1,pt2 = self.find_longest(hull)
			img_out,rapport = self.draw_back(hull,pt1,pt2,img)

		else :
			img_out,rapport = self.draw_line(hull,img)
		return img_out, rapport


	def calcul_rapport(self,longueur,maxi):
		return maxi/longueur

	def find_bigest(self,contour,hierarchy):
		"""
		contour est un tableau contenant les positions des points des differents objets de l'image
		hierarchy contient des le meme tableau, mais au lieu des coords on a des caracteristiques des objets,
		par ex en pos 3 on a un chiffre decrivant cet objet, a savoir si il est englobe ou non par un autre
		celui en -1 est le pere de tous, chez nous c'est le contour de l'image
		Nous on veut donc le deuxieme echelon 0 donc
		Ensuite contourArea nous donne l'aire des objects, on choisis donc le plus gros (le poisson a priori et pas les saletes)
		et on recupere sa position dans la liste des objets pour pouvoir en calculer l'enveloppe convexe par la suite.
		"""
		maxi = 0
		pos = 0
		for num in range(len(contour)):
			if hierarchy[0][num][3] == 0:
				area = cv2.contourArea(contour[num])
				if area > maxi:
					maxi = area
					pos = num
		return pos

	def find_longest(self,points):
		maxi = 0
		for i in range(len(points)):
			for j in range(len(points)):
				distance = self.calcul_distance(points,i,j)
				if distance > maxi:
					maxi = distance
					pt1 = i
					pt2 = j
		return pt1,pt2

	def save(self,donnee,nom):
		fic = open ('../result/save.csv', "a")
		fic.write(nom)
		fic.write(',')
		fic.write(str(donnee))
		fic.write ('\n')

	def processing(self):
		hist = cv2.calcHist([self.img],[0],None,[256],[0,256])
		self.gaussianBlur(self.img)
		tresh = self.triangle(hist)
		self.treshold(self.img,tresh)
		self.fill_holes(self.img)
		contour,hierarchy = cv2.findContours(self.img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		interest = contour[self.find_bigest(contour,hierarchy)]
		hull = cv2.convexHull(interest)
		ellipse = cv2.fitEllipse(interest)
		elongation = self.calc_ellipse(ellipse)
		self.cop,rapport = self.drawEllipse(hull,self.cop,elongation)
		self.save(rapport,self.name)
		cv2.imwrite("../result/"+self.name+".jpg",self.cop)


def create_save():
	fic = open ('../result/save.csv', "w")
	fic.write('image_name')
	fic.write(',')
	fic.write('fish_circularity')
	fic.write('\n')
	
def main(directory):
	imagesPool = []
	os.chdir(directory)
	create_save()
	for element in os.listdir(directory):
		print element
		imagesPool.append(Image_zebra(element))
	
	""" applying algorithms on each image in the previous list """ 	
	for pic in imagesPool:
		pic.processing()


		
