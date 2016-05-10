import sys,os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Widget(QWidget):

    def __init__(self, parent= None):
        super(Widget, self).__init__()

        #Container Widget       
        self.widget = QWidget()
        #Layout of Container Widget
        self.layout = QGridLayout()
	self.widget.setLayout(self.layout)
    
        

        #Scroll Area Properties
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        #Scroll Area Layer add
        self.vLayout = QGridLayout()

        self.vLayout.addWidget(self.scroll)
        self.setLayout(self.vLayout)

    def showImages(self,directory):
	j=0
	i=0
	for element in os.listdir(directory):
		size=400
		icon=QIcon()
		mode=QIcon.Normal
		state=QIcon.Off
		pixma = QPixmap(directory+"/"+element) 
		icon.addPixmap(pixma,mode,state)
		label = QLabel()
		label.setPixmap(icon.pixmap(size,QIcon.Normal,state))
       		self.layout.addWidget(label,i,j)
		j+=1
		if j%3 == 0:
			i+=1
			j=0
			


