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
		
def draw_roundFish(points,img):
	"""
	on commence par calculer la plus grande distance entre deux points successifs et on considerera que ce sont les points de la tete et de la queue.
	puis on dessine une ligne entre chaque points pour dessiner le dos du poisson
	On dessine egalement un trait entre le premier et le dernier point de la liste.
	"""
	maxi = 0
	for i in range(len(points)-1):
		distance = calcul_distance(points,i,i+1)
		
		if distance > maxi :
			maxi = distance
			top = i
			bot = i+1

	longueur, img = drawing(points,0,len(points)-1,1,maxi,img)

	dst = calcul_distance(points,0,-1)
	if dst < maxi:
		cv2.line(img,(points[0][0][0],points[0][0][1]),(points[-1][0][0],points[-1][0][1]),(255,0,0),1)
		longueur += dst
	
	rapport = calcul_rapport(longueur,maxi)

	return img,rapport,top,bot

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

def find_longest(points):
	maxi = 0
	for i in range(len(points)):
		for j in range(len(points)):
			distance = calcul_distance(points,i,j)
			if distance > maxi:
				maxi = distance
				pt1 = i
				pt2 = j
	return pt1,pt2

def calcul_rapport(longueur,maxi):
	return maxi/longueur

def calcul_distance(points,xa,xb):
	dstx = points[xa][0][0] - points[xb][0][0] # = Xa - Xb
	dsty = points[xa][0][1] - points[xb][0][1] # = Ya - Yb
	distance = sqrt(pow(dstx,2) + pow(dsty,2))
	return distance

def draw_longFish(contour,hull,top,bot,img):
	"""
	on creer une nouvelle image noire de la meme taille que la photo, puis on trace l'envellope convexe
	entre top et bot ainsi que le contour entre top et bot egalement.
	Puis on analyse cette image et on calcule l'aire du dessin qu'on vient de faire 
	"""
	img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img1 = np.zeros(img_gray.shape, np.uint8)
	img2 = np.zeros(img_gray.shape, np.uint8)

	# Il faut retrouver quels points de contour ont les memes coordonnees que top et bot
	for i in range(len(contour)):

		if contour[i][0][0] == hull[top][0][0] and contour[i][0][1] == hull[top][0][1] :
			top_contour = i

	for j in range(len(contour)):
		if contour[j][0][0] == hull[bot][0][0] and contour[j][0][1] == hull[bot][0][1]:
			bot_contour = j

	# on fait des tests pour pouvoir dessiner les 2 contours dans le bon sens
	"""
	if top_contour > bot_contour and top > bot:
		poubelle,imga = drawing(contour,bot_contour,top_contour,1,1000000,img1)
		longueurb,imga = drawing(hull,bot,top,1,1000000,img1)
		#inversion des point pour dessiner de l'autre cote du poisson
		invert_top_contour = top_contour - len(contour)
		invert_top = top - len(hull)
		poubelle,imgb = drawing(contour,bot_contour,invert_top_contour ,-1,1000000,img2)
		longueurb,imgb = drawing(hull,bot,invert_top,-1,1000000,img2)
	"""
	if top_contour > bot_contour and top < bot:
		# Ici je me suis rendu compte qu'on tracait l'enveloppe dans un sens et le contour dans l'autre, donc j'ai inverse les lignes
		# pour dessiner du meme cote
		invert_bot = bot - len(hull)
		poubelle,imgb = drawing(contour,bot_contour,top_contour,1,1000000,img1)
		longueurb,imgb = drawing(hull,top,invert_bot,-1,1000000,img1)
		#inversion des point pour dessiner de l'autre cote du poisson
		invert_top_contour = top_contour - len(contour)
		poubelle,imga = drawing(contour,bot_contour,invert_top_contour ,-1,1000000,img2)
		longueurb,imga = drawing(hull,top,bot,1,1000000,img2)
		
	"""
	if bot_contour > top_contour and top > bot:
		poubelle,imga = drawing(contour,top_contour,bot_contour,1,1000000,img1)
		longueurb,imga = drawing(hull,bot,top,1,1000000,img1)
		#inversion des point pour dessiner de l'autre cote du poisson
		invert_bot_contour = bot_contour - len(contour)
		invert_bot = bot - len(hull)
		poubelle,imgb = drawing(contour,top_contour,invert_bot_contour ,-1,1000000,img2)
		longueurb,imgb = drawing(hull,top,invert_bot,-1,1000000,img2)
	"""
	if  top_contour < bot_contour and top < bot:
		poubelle,imga = drawing(contour,top_contour,bot_contour,1,1000000,img1)
		longueura,imga = drawing(hull,top,bot,1,1000000,img1)
	
		#inversion des point pour dessiner de l'autre cote du poisson
		invert_bot_contour = bot_contour - len(contour)
		invert_bot = bot - len(hull)
		poubelle,imgb = drawing(contour,top_contour,invert_bot_contour ,-1,1000000,img2)
		longueurb,imgb = drawing(hull,top,invert_bot,-1,1000000,img2)
	
	
	# puis on calcule les aires des dessins obtenus pour les comparer
	img_contoura = imga.copy()
	contour,hierarchy = cv2.findContours(img_contoura,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	areaA = cv2.contourArea(contour[0])

	img_contourb = imgb.copy()
	contour,hierarchy = cv2.findContours(img_contourb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	areaB = cv2.contourArea(contour[0])
	#enfin on trace le contour voulu sur la photo
	if areaA < areaB :
		longueur,img = drawing(hull,top,bot,1,1000000,img)
		
	
	else :
		invert_bot = bot - len(hull)
		longueur,img = drawing(hull,top,invert_bot,-1,1000000,img)
		
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	
	# on calcule la distance entre les deux points opposes pour obtenir la distance "a vol d'oiseau" 

	maxi = calcul_distance(hull,bot,top)
	rapport = calcul_rapport(longueur,maxi)
	return img,rapport

def drawing(points,pt1,pt2,pas,maxi,img):
	"""
	Ici, on dessine sur une image une ligne droite entre chaque points de "points" compris entre
	pt1 et pt2
	"""
	longueur = 0
	i = pt1
	while i != pt2 :
		dst = calcul_distance(points,i,i+1)
		
		if dst < maxi : 
			cv2.line(img,(points[i][0][0],points[i][0][1]),(points[i+1][0][0],points[i+1][0][1]),(255,0,0),1)
			longueur += dst
		#else:
		#	return 0,None

		i += pas		
	return longueur,img

def draw_backContour(hull,img,ellipse,contour):
	"""
	Fonction qui permet de decider si on a un poisson de type long ou rond.
	Cela se fait en calculant le rapport de la largeur sur la longueur de l'ellipse
	obtenue avec fitEllipse.
	elle va ensuite lancer en fonction, soit la fonction draw_longFish, soit draw_roundfsh.
	"""

	ovality = calc_ellipse(ellipse)
	if ovality < 0.5:
		pt1,pt2 = find_longest(hull)
		img_out,courbure = draw_longFish(contour,hull,pt1,pt2,img)
		img_out = detect_yolk(img_out,img, 250, 100)
	else :
		img_out,courbure,pt1,pt2 = draw_roundFish(hull,img)
		img_out = detect_yolk(img_out,img,400,60)
	return img_out, courbure,pt1,pt2

def calc_ellipse(ellipse):
	rapport = ellipse[1][0]/ellipse[1][1]
	return rapport

def detect_yolk(img,img_out, par1, par2):

	"""
	details parametres de la fonction houghcircles :
	-- cv2.cv.CV_HOUGH_GRADIENT : unique methode utilisee definit la methode pour detecter les cercles

	-- dp : c'est le ratio inverse de la resolution accumulee dans limage si dp=1 la resolution est la meme que l'image en entree plus le dp est eleve plus lobtention de cercle est importante

	--mindist: distance min entre le centre des cercles detecte plus il est petit plus de cercles sont detectes si trop grand alors certains milieux ne peuvent pas etre detectes

	--param1 gere la detection de bord

	--param2 plus le seuil est grand plus les cercles sont dectetes 

	"""
	cimg = cv2.medianBlur(img,5)
	cimg = cv2.cvtColor(cimg, cv2.COLOR_BGR2GRAY)

	circles = cv2.HoughCircles(cimg,cv2.cv.CV_HOUGH_GRADIENT,1,par1,param1=par2,param2=30,minRadius=5,maxRadius=1000)


	"""
	parametre detection de loeil:

	(img,cv2.cv.CV_HOUGH_GRADIENT,1,40,param1=50,param2=30,minRadius=10,maxRadius=55)

	exception
	z05/z10 : (img,cv2.cv.CV_HOUGH_GRADIENT,2,500,param1=50,param2=30,minRadius=10,maxRadius=55)

	fonctionne pas:
	z07 (img,cv2.cv.CV_HOUGH_GRADIENT,2,300,param1=20,param2=98,minRadius=5,maxRadius=60)
	z08a

	"""

	"""
	parametre detection du yolk:

	#parametre pour les poissons long img,cv2.cv.CV_HOUGH_GRADIENT,1,250,param1=100,param2=30,minRadius=5,maxRadius=1000)

	#parmetre pour les poissons rond  img,cv2.cv.CV_HOUGH_GRADIENT,1,400,param1=60,param2=30,minRadius=5,maxRadius=1000)

	#exception lorsque le bout du yolk est trop marque 
	(img,cv2.cv.CV_HOUGH_GRADIENT,100,600,param1=100,param2=30,minRadius=5,maxRadius=1000)
	"""


	circles = np.uint16(np.around(circles))


	for i in circles[0,:]:
		cv2.circle(img_out,(i[0],i[1]),i[2],(127, 255, 212),1)  # dessine le cercle
		cv2.circle(img_out,(i[0],i[1]),2,(0,0,255),3)     # dessine le centre du cercle

	return img_out


