#!/usr/bin/env python
#!coding:utf-8

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Image_processing as imp
import widget as wg

class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()
	self.resultDir = "../Analyze_results/Images/"
	self.w = wg.Widget()
        self.setCentralWidget(self.w)	
        self.createActions()
        self.createMenus()
        self.directory = ""
        self.setWindowTitle("ZebraFish Analyzer")
        self.resize(800, 640)
		
    def open(self):
		self.directory = QFileDialog.getExistingDirectory(self)
		print self.directory
		
    def analyze(self):
		if self.directory:
			imp.process_all_images(str(self.directory))
			self.w.showImages(self.resultDir)
		else:
			print "pas de répertoire sélectionné"

    def createActions(self):
		self.openAct = QAction("&Open", self, shortcut="Ctrl+O",triggered=self.open)
		self.analyzeAct = QAction("&Analize", self, shortcut="Ctrl+A",triggered=self.analyze)

        
    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.analyzeAct)
        self.menuBar().addMenu(self.fileMenu)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    imageViewer = ImageViewer()
    imageViewer.show()	
    sys.exit(app.exec_())
