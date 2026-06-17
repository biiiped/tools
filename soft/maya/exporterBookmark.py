
import os
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
        self.button1 = QtWidgets.QPushButton("export book mark")
        self.button2 = QtWidgets.QPushButton("import book mark")



    def createLayout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.button1)
        main_layout.addWidget(self.button2)
    
    def create_connections(self):
        self.button1.clicked.connect(self.exportBookmark)
        self.button2.clicked.connect(self.select_nodes_from_file)

    def exportBookmark(self):
        sl = cmds.ls(sl=1)
        self.file_path = r"C:\Users\l.bonnaud\Desktop\bookmark.txt"
        print(f"printing on : {self.file_path}")
        with open(self.file_path, 'w') as file:
            # Write some text to the file
            for node in sl:  # Added a colon here
                file.write(str(node)+"\n")

    def select_nodes_from_file(self):
        print("select_nodes_from_file")
        self.file_path = r"C:\Users\l.bonnaud\Desktop\bookmark.txt"

        with open(file_path, 'r') as file:
            node_names = file.read().splitlines()
            print(str(node_names))

        for node_name in node_names:
            print(node_name)
            if cmds.objExists(node_name):
                cmds.select(node_name, add=True)
                print(f"selecting : {node_name}")
            else:
                print(f"Node '{node_name}' does not exist in the scene.")


def bookMarkExporter():
    if __name__ == "__main__":

        d = TestDialog()
        d.show()

bookMarkExporter()

