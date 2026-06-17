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
        
        self.label1 = QtWidgets.QLabel("Proxy attribute !")
        self.label2 = QtWidgets.QLabel("Proxy attribute name:")
        self.lineedit1 = QtWidgets.QLineEdit('IKFK')
        self.label3 = QtWidgets.QLabel("Attribute path:")
        self.lineedit2 = QtWidgets.QLineEdit('optionCtl_arm_R.IKFK')
        self.addProxyAttrButton = QtWidgets.QPushButton("add proxy attr")
        self.separatorButton = QtWidgets.QPushButton("add separator")


    def createLayout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.label1)
        main_layout.addWidget(self.label2)
        main_layout.addWidget(self.lineedit1)
        main_layout.addWidget(self.label3)
        main_layout.addWidget(self.lineedit2)
        main_layout.addWidget(self.addProxyAttrButton)
        main_layout.addWidget(self.separatorButton)
    
    def create_connections(self):
        self.separatorButton.clicked.connect(self.add_separator)
        self.addProxyAttrButton.clicked.connect(self.add_proxy_attr_button)

    def add_separator(self):
        print("adding a separator")
        sl=cmds.ls(sl=1)
        cmds.addAttr(ln='______',en='______',k=1,at='enum')
    
    def add_proxy_attr_button(self):
        sl=cmds.ls(sl=1)

        proxyAttributeName=self.lineedit1.text()
        attributePath=self.lineedit2.text()
        print(proxyAttributeName)
        print(attributePath)
        cmds.addAttr(ln=proxyAttributeName,proxy=attributePath)



if __name__ == "__main__":

    d = TestDialog()
    d.show()


