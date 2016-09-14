#!usr/bin/env python3

"""
Basic Display Rpeating readouts on Pressure assisted 



"""

import sys
from PyQt4 import QtGui, QtCore

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50,50,500,300)
        self.setWindowTitle("PyQT Tutorial")
        #self.setWindowIcon(QrGui.QIcon(''))

        #file menu choices
        closeAction = QtGui.QAction("&Quit",self)
        closeAction.setShortcut("Ctrl+Q")  #set keyboard shortcut
        closeAction.setStatusTip('Leave the App')
        closeAction.triggered.connect(self.close_application)

        #setupMenu choices

        
        #setup menubar
        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(closeAction)

        setupMenu = mainMenu.addMenu('&Setup')
        
        
        #Call home view
        self.statusBar()
        self.home()

    def home(self):
        btn = QtGui.QPushButton("Quit", self)
        btn.clicked.connect(self.close_application)
        btn.resize(btn.sizeHint())
        btn.move(100,100)

        self.show()
        
    def close_application(self):
        choice = QtGui.QMessageBox.question(self, 'Quit',
                                            'Are you sure you want to quit?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass


def run():
    
    app = QtGui.QApplication(sys.argv)
    GUI = Window()


    
    sys.exit(app.exec_())


run()
        



