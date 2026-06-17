import sys

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds

"""ce script prends un hierarchie de joint et créé sa hierarchie de controllers"""

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class TestDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(TestDialog, self).__init__(parent)
        self.setWindowTitle("Test Dialog")
        self.setMinimumWidth(200)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.createWidget()
        self.createLayout()
        self.create_connections()

    def createWidget(self):
        self.label1 = QtWidgets.QLabel("select your poo")
        self.lineedit1 = QtWidgets.QLineEdit('skinCluster1')
        self.lineedit2 = QtWidgets.QLineEdit('1')
        self.button = QtWidgets.QPushButton("skin !")



    def createLayout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.label1)
        main_layout.addWidget(self.lineedit2)
        main_layout.addWidget(self.lineedit1)
        main_layout.addWidget(self.button)
    
    def create_connections(self):
        self.button.clicked.connect(self.skinPoint)

    def skinPoint(self):
        skinCluster=self.lineedit1.text()
        strengh=float(self.lineedit2.text())

        sl=cmds.ls(sl=1)
        joint=sl.pop()

        print("assigning with a influence of 1 these points:")
        print(sl)
        print("to this joint:")
        print(joint)
        cmds.skinPercent( skinCluster, sl, transformValue=[(joint, strengh)])

def mechaSkining():
    if __name__ == "__main__":

        d = TestDialog()
        d.show()


