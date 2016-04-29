from math import *
import numpy as np
import cv2

def gaussianBlur(img):
		""" apply a blur to the image img
		impair values required for radius """
		return cv2.GaussianBlur(img,(5,5),9)
	
def treshold(img,tresh):
		ret,img = cv2.threshold(img,tresh,255,cv2.THRESH_BINARY)
		return img
		

def triangle(data):
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

def fill_holes(img):
		#filling holes (je ne sait pas ce qu'il se passe)
		des = cv2.bitwise_not(img)
		contour,hier = cv2.findContours(des,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
	
		for cnt in contour:
			cv2.drawContours(des,[cnt],0,255,-1)
		#inversion des couleur
		img = cv2.bitwise_not(des)
		return img
		
def draw_line(points,img):
		# on commence par calculer la plus grande distance entre deux points successifs et on considerera que ce sont les points de la tete et de la queue.
		maxi = 0
		for i in range(len(points)-1):
			dstx = points[i][0][0] - points[i+1][0][0] # = Xa - Xb
			dsty = points[i][0][1] - points[i+1][0][1] # = Ya - Yb
			distance = sqrt(pow(dstx,2) + pow(dsty,2))
	
			if distance > maxi :
				maxi = distance
	
		# dessine une ligne entre deux opints
		#on calcule d'abord la distance entre deux points successifs, et si elle est inferieure a 200px (arbitraire) on trace la ligne
		for i in range(len(points)-1):
			dstx = points[i][0][0] - points[i+1][0][0] # = Xa - Xb
			dsty = points[i][0][1] - points[i+1][0][1] # = Ya - Yb
	
			if sqrt(pow(dstx,2) + pow(dsty,2)) < maxi :  # = racine carree ((xa-xb) + (ya-yb))
				cv2.line(img,(points[i][0][0],points[i][0][1]),(points[i+1][0][0],points[i+1][0][1]),(190,50,0),2)
	
		dstx = points[0][0][0] - points[-1][0][0]
		dsty = points[0][0][1] - points[-1][0][1]
		if sqrt(pow(dstx,2) + pow(dsty,2)) < maxi:
			cv2.line(img,(points[0][0][0],points[0][0][1]),(points[-1][0][0],points[-1][0][1]),(190,50,0),2)
		return img

def find_bigest(contour,hierarchy):
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




