import nuke
import re



def main_function():
    from PySide2.QtWidgets import QWidget,QLabel,QPushButton,QVBoxLayout,QCheckBox,QHBoxLayout
    import json
    import random
    import os
    nuke.root().knob('colorManagement').setValue("OCIO")

    def getFrameRange(shID):
        with open(r"\\MINERVA\3d4_23_24\MECHA\02_ressource\@LOUIS\ressources\thumbnail\timeRanges.json", 'r') as file:
            data = json.load(file)
        if shID in data:
            values = data[shID]
            return (values)
        else:
            return [0,0]
    
    def findExrFolders(base_directory):
            exr_folders = []
            
            for root, dirs, files in os.walk(base_directory):
                for dir_name in dirs:
                    if dir_name.endswith('_exr'):
                        exr_folders.append(os.path.join(root, dir_name))
            return exr_folders
    
    def create_read(name,path,startFrame,endFrame,x,y):
            print(f"creating {name}")
            readNode=nuke.createNode('Read')
            readNode.setName(name)
            readNode['file'].setValue(path)
            readNode["first"].setValue(startFrame)
            readNode["last"].setValue(endFrame)
            readNode["origfirst"].setValue(startFrame)
            readNode["origlast"].setValue(endFrame)
            readNode["on_error"].setValue("error")
            readNode.setXpos(x)
            readNode.setYpos(y)
            return readNode

    def create_write(name,path,input,x,y):
            print(f"creating {name}")
            writeNode=nuke.createNode('Write')
            writeNode.setName(name)
            writeNode['file'].setValue(path)
            writeNode.setXpos(x)
            writeNode.setYpos(y)
            writeNode['mov64_codec'].setValue("h264")
            writeNode['create_directories'].setValue(1)
            writeNode['colorspace'].setValue("color_picking")
            #self.shotNodes.append(writeNode)
            return writeNode       
    
 
    base_directory="//MINERVA/3d4_23_24/MECHA/08_editing/input/06_compo"
    exrDir=findExrFolders(base_directory)
    print(exrDir)
    n=0
    x=0
    for shotFolder in exrDir:
                base_name = os.path.basename(shotFolder)
                shID = base_name.replace('_exr', '')
                shID = shID.replace('MCH_', '')
                print(shID)
                frameRange=getFrameRange(shID)
                name=f"MCH_{shID}_####.exr"
                path=os.path.join(shotFolder,name)
                path=path.replace("\\", "/")
                readNode=create_read(shID,path,frameRange[0],frameRange[1],n,x)
                
                
                if "seq010" in shotFolder:
                    R, G, B = 0.5, 0.5, 1.0
                    color_value = (int(R * 255) << 24) + (int(G * 255) << 16) + (int(B * 255) << 8) + 1
                    readNode['tile_color'].setValue(color_value)
                if "seq020" in shotFolder:
                    R, G, B = 0.2, 0.2, 1.0
                    color_value = (int(R * 255) << 24) + (int(G * 255) << 16) + (int(B * 255) << 8) + 1
                    readNode['tile_color'].setValue(color_value)
                if "seq030" in shotFolder:
                    R, G, B = 0.8, 0.2, 1.0
                    color_value = (int(R * 255) << 24) + (int(G * 255) << 16) + (int(B * 255) << 8) + 1
                    readNode['tile_color'].setValue(color_value)
                if "seq040" in shotFolder:
                    R, G, B = 0.2, 0.8, 1.0
                    color_value = (int(R * 255) << 24) + (int(G * 255) << 16) + (int(B * 255) << 8) + 1
                    readNode['tile_color'].setValue(color_value)
            
                outPath=f"//MINERVA/3d4_23_24/MECHA/08_editing/input/13_compo_mov/{shID}.mov"
                create_write(shID+"_write",outPath,readNode,n,x+101)
                x=x+random.randint(-50, 50)
                n+=101
main_function()