import nuke
import os
import re
import json



def main_function():
    from PySide2.QtWidgets import QWidget,QLabel,QPushButton,QVBoxLayout
    import json

    class SimpleWindow(QWidget):
        def __init__(self):
            super(SimpleWindow, self).__init__()
            self.setWindowTitle("Simple PySide2 Window in Nuke")
            self.setMinimumWidth(300)

            self.create_widgets()
            self.layout_widgets()

        def create_widgets(self):
            self.label = QLabel("Hello from PySide2!")
            self.button = QPushButton("OK")
            self.button.clicked.connect(self.close)

        def layout_widgets(self):
            layout = QVBoxLayout()
            layout.addWidget(self.label)
            layout.addWidget(self.button)
            layout.addStretch(1)
            self.setLayout(layout)
        
#-------------------------------------------
        def create_ui(self,sequence):
            shotList=[]
            shots=os.listdir(f"//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render/{sequence}")
            for shot in shots:
                shotList.append(sequence+"_"+shot)
            # Create a new panel (group)
            p = nuke.Panel("Check Cases Example")
            
            # Add checkboxes to the panel
            for shot in shotList:
                p.addBooleanCheckBox(shot, False)

            return p.show()        

        def getFrameRange(self,seqID,shID):
            shotName=seqID+"_"+shID
            with open(r"\\MINERVA\3d4_23_24\MECHA\02_ressource\@LOUIS\ressources\thumbnail\timeRanges.json", 'r') as file:
                data = json.load(file)
            if shotName in data:
                values = data[shotName]
                
                return (values)

        def get_last_shot_version(self,seqID, shID):

            path1 = f"//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render/{seqID}/{shID}"
            try:
                items = os.listdir(path1)
                # Define a function to extract the numerical part of the strings
                def extract_number(s):
                    try:
                        return int(s[1:])
                    except Exception as e:
                        return 1
                      # Remove the 'v' and convert the rest to an integer
                # Sort the list using the custom key
                sorted_list = sorted(items, key=extract_number)
                maxVersion=sorted_list[-1]
                return maxVersion
            except Exception as e:
                print(e)
                return "no version find"

        def create_read(self,name,path,startFrame,endFrame):
            print(f"creating {name}")
            readNode=nuke.createNode('Read')
            readNode.setName(name)
            readNode['file'].setValue(path)
            readNode["first"].setValue(startFrame)
            readNode["last"].setValue(endFrame)
            readNode["origfirst"].setValue(startFrame)
            readNode["origlast"].setValue(endFrame)
            readNode.setXpos(0)
            readNode.setYpos(0)

        def create_merge(self,name,inputA,inputB,output):
            print(f"creating {name}")

        def main(self):
            lastVersion=self.get_last_shot_version(seqID,shID)
            print(f"lastVersion= {lastVersion}")
            shotFolder=f"//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render/{seqID}/{shID}/{lastVersion}"
            renderLayers = os.listdir(shotFolder)

            for renderLayer in renderLayers:
                print(f"renderLayer= {renderLayer}")

                renderLayerPath=f"//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render/{seqID}/{shID}/{lastVersion}/{renderLayer}/{seqID}_{shID}_{renderLayer}_aov_{lastVersion}_%04d.exr"
                renderLayerNodeName=f"{seqID}_{shID}_{renderLayer}_aov_{lastVersion}"
                frameRange=self.getFrameRange(seqID,shID)

                self.create_read(renderLayerNodeName,renderLayerPath,frameRange[0],frameRange[1])
                #create_merge(name,inputA,inputB,output)

            #creating write
            writePath=f"//MINERVA/3d4_23_24/MECHA/08_editing/input/08_assemblage/{seqID}/{shID}/{seqID}_{shID}_assemblage.mp4"
            print(f"Write path: {writePath}")

    def show_window():
        global custom_window
        try:
            custom_window.close()
        except:
            pass

        custom_window = SimpleWindow()
        custom_window.show()

    show_window()

main_function()