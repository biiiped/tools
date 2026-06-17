import sys
import os
import shutil

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel



MCH_assets = {
    "extracteur": ["grosExtracteur_geo"],

    "shark": ["geo_shark","MCH_chr_shark_rig_P:geo_shark"],
    "sharkLight": ["lightLocs_shark","MCH_chr_shark_rig_P:lightLocs_shark"],

    "goliath": ["geo_goliath"],
    "goliathLight": ["light_locator"],

    "missile1": ["MCH_prp_missiles_rig_P:missile_geo","missile|missile_geo"],
    "missile2": ["MCH_prp_missiles_rig_P1:missile_geo","missile1|missile_geo"],
    "missile3": ["MCH_prp_missiles_rig_P2:missile_geo","missile2|missile_geo"],
    "missile4": ["MCH_prp_missiles_rig_P3:missile_geo","missile3|missile_geo"],
    "missile5": ["MCH_prp_missiles_rig_P4:missile_geo","missile4|missile_geo"],
    "missile6": ["MCH_prp_missiles_rig_P5:missile_geo","missile5|missile_geo"],
    "missile7": ["MCH_prp_missiles_rig_P6:missile_geo","missile6|missile_geo"],
    "missile8": ["MCH_prp_missiles_rig_P7:missile_geo","missile7|missile_geo"],
    "obus": ["MCH_prp_obus_rig_P:Obus","obus_geo","MCH_prp_obus_rigNotrail_P:obus_geo"],

    "missile1LgtLoc": ["MCH_prp_missiles_rig_P:missileLightLocator","missile|missileLightLocator"],
    "missile2LgtLoc": ["MCH_prp_missiles_rig_P1:missileLightLocator","missile1|missileLightLocator"],
    "missile3LgtLoc": ["MCH_prp_missiles_rig_P2:missileLightLocator","missile2|missileLightLocator"],
    "missile4LgtLoc": ["MCH_prp_missiles_rig_P3:missileLightLocator","missile3|missileLightLocator"],
    "missile5LgtLoc": ["MCH_prp_missiles_rig_P4:missileLightLocator","missile4|missileLightLocator"],
    "missile6LgtLoc": ["MCH_prp_missiles_rig_P5:missileLightLocator","missile5|missileLightLocator"],
    "missile7LgtLoc": ["MCH_prp_missiles_rig_P6:missileLightLocator","missile6|missileLightLocator"],
    "missile8LgtLoc": ["MCH_prp_missiles_rig_P7:missileLightLocator","missile7|missileLightLocator"],
    "obusLgtLoc": ["MCH_prp_obus_rig_P:obusLocLight","obusLocLight","MCH_prp_obus_rigNotrail_P:obusLocLight"],
    
    "sword": ["sword_geo"],

    "tube A": ["tube_A"],
    "tube B": ["tube_B"],
    
    "dock": ["moving_dock_geo"],

    #"goliathProxy": ["geo_goliath_proxy"],
    "citerne": ["geo_citerne_goliath"],
    "rick": ["MCH_asset_char_rick","MCH_chr_rick_rig_P:MCH_asset_char_rick"],
    "zeke": ["MCH_asset_char_zeke"],
    "cockpit": ["geo_cockpit"],
    "camera": ["shotCam"],
}
cache_directory=r"\\MINERVA\3d4_23_24\MECHA\11_cache"

def get_maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



class mainWindow(QtWidgets.QDialog):

    def __init__(self, parent=get_maya_main_window()):
        super(mainWindow, self).__init__(parent)
        self.setWindowTitle("USD publish Anim")
        self.setMinimumWidth(200)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        
        self.createWidget()
        self.createLayout()
        self.create_connections()
        
    
    def createWidget(self):
        self.separator1=self.create_separator()
        self.helloMessage = QtWidgets.QLabel("anim publish !")
        self.separator2=self.create_separator()
        self.labelStartFrame = QtWidgets.QLabel("labelStartFrame")
        self.labelEndFrame = QtWidgets.QLabel("labelEndFrame")
        self.scene_start_frame,self.scene_end_frame=self.get_scene_frame_range()
        self.lineeditStartFrame = QtWidgets.QLineEdit(str(int(self.scene_start_frame)))
        self.lineeditEndFrame = QtWidgets.QLineEdit(str(int(self.scene_end_frame)))
        self.separator2=self.create_separator()
        self.separator3=self.create_separator()
        self.lineeditComment = QtWidgets.QLineEdit("")
        self.folderBtn = QtWidgets.QPushButton("open publish folder")
        self.rappelMessage = QtWidgets.QLabel("""
attention , la camera doit etre nommee 'shotCam'
et doit etre dans un groupe 'camera' lui meme dans
groupe 'camRig'
                                              
CamRig
   - camera
      - shotCam""")
        self.publishBtn = QtWidgets.QPushButton("publish")

    def createLayout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.Chckbox_layout = QtWidgets.QVBoxLayout(self)
        StartFrame_layout = QtWidgets.QHBoxLayout()
        StartFrame_layout.addWidget(self.labelStartFrame)
        StartFrame_layout.addWidget(self.lineeditStartFrame)
        EndFrame_layout = QtWidgets.QHBoxLayout()
        EndFrame_layout.addWidget(self.labelEndFrame)
        EndFrame_layout.addWidget(self.lineeditEndFrame)
        self.main_layout.addWidget(self.helloMessage)
        self.main_layout.addWidget(self.separator1)
        self.main_layout.addLayout(StartFrame_layout)
        self.main_layout.addLayout(EndFrame_layout)
        self.main_layout.addWidget(self.separator3)
        self.Chckbox_Names= self.create_assets_boxs()

        checkbox_container = QtWidgets.QWidget()
        checkbox_container.setLayout(self.Chckbox_layout)

        # Create a QScrollArea
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(checkbox_container)
        scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(scroll_area)

        self.main_layout.addWidget(self.separator2)
        self.main_layout.addWidget(self.rappelMessage)
        self.main_layout.addWidget(self.lineeditComment)
        self.main_layout.addWidget(self.publishBtn)
        self.main_layout.addWidget(self.folderBtn)

    def create_connections(self):
        self.publishBtn.clicked.connect(self.publish)
        self.folderBtn.clicked.connect(self.openFolder)

    def create_assets_boxs(self):
        detectedAssets=self.detectAssets()
        Chckbox_Names=[]
        if detectedAssets:
            for asset in detectedAssets:
                Chckbox_Name=self.create_asset_box(asset)
                Chckbox_Names.append(Chckbox_Name)
        else:
            self.nothinglabel=QtWidgets.QLabel(f"nothing is detected :(")
            self.main_layout.addWidget(self.nothinglabel)
        return Chckbox_Names
    
    def create_asset_box(self,asset):
        for key, values in MCH_assets.items():
            for value in values:
                if value == asset:
                    desired_key = key
                    break
        label=QtWidgets.QLabel(f"{desired_key} detected !")
        Chckbox = QtWidgets.QCheckBox(asset)
        Chckbox.setChecked(True)
        asset_box_layout = QtWidgets.QVBoxLayout(self)

        asset_box_layout.addWidget(label)
        asset_box_layout.addWidget(Chckbox)
        asset_box_layout.addSpacing(20)
        self.Chckbox_layout.addLayout(asset_box_layout)
        return Chckbox

    def create_separator(self):
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        return separator

    def get_scene_frame_range(self):
    
        scene_start_frame = cmds.playbackOptions(q=True, animationStartTime=True)
        scene_end_frame = cmds.playbackOptions(q=True, animationEndTime=True)
        return scene_start_frame, scene_end_frame

# Get scene frame range
    def detectAssets(self):
        detectedAssets=[]
        for asset,geoAssets in MCH_assets.items():
            for geoAsset in geoAssets:
                if cmds.objExists(geoAsset):
                    print(f"Found {geoAsset} in the outliner.")
                    detectedAssets.append(geoAsset)
                else:
                    print(f"No {geoAsset} found in the outliner.")
        print(f" detectedAssets{detectedAssets}")
        return detectedAssets

    def get_publish_file_name(self,asset):

        for key, values in MCH_assets.items():
            for value in values:
                if value == asset:
                    desired_key = key
                    break

        # Get the name of the file
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        scene_name_splitted = scene_name.split('_')
        sequence=scene_name_splitted[1]
        shot=scene_name_splitted[2]

        publish_dir=os.path.join(cache_directory,sequence,shot,)

        publish_file_name=f"MCH_{sequence}_{shot}_{desired_key}_anim"
        
        return publish_file_name, publish_dir
    
    def show_error_message(self, message):
        error_box = QtWidgets.QMessageBox()
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setText("Error")
        error_box.setInformativeText(message)
        error_box.setWindowTitle("Error")
        error_box.exec_()
   
    def show_info_message(self, message):
        info_box = QtWidgets.QMessageBox()
        info_box.setIcon(QtWidgets.QMessageBox.Information)
        info_box.setText("Information")
        info_box.setInformativeText(message)
        info_box.setWindowTitle("Information")
        info_box.exec_()


    def export_abc(self,asset, publish_file_name, UI_start_frame, UI_end_frame):


        cmds.select(asset, r=True) # Select the shot cam
        command = f"-frameRange {UI_start_frame} {UI_end_frame} -worldSpace -root {asset} -file {publish_file_name}.abc"
        cmds.AbcExport ( j = command )
        cmds.select(clear=True)


    def exportUSD(self,asset, publish_file_name, UI_start_frame, UI_end_frame):

        cmds.select(asset, r=True) # Select the correct export geometry
        if cmds.getAttr(asset + ".visibility") == False:
            cmds.setAttr(asset + ".visibility", True)


        reversed_path = publish_file_name.replace('\\', '/')
        USD_publish_string = (
            f'file -force -options"'
            f';exportUVs=1;'
            f'exportSkels=none;'
            f'exportSkin=none;'
            f'exportBlendShapes=0;'
            f'exportDisplayColor=0;'
            f'exportColorSets=0;'
            f'exportComponentTags=1;'
            f'defaultMeshScheme=catmullClark;'
            f'animation=1;'
            f'eulerFilter=0;'
            f'staticSingleSample=0;'
            f'startTime={UI_start_frame};'
            f'endTime={UI_end_frame};'
            f'frameStride=1;frameSample=0.0;'
            f'defaultUSDFormat=usdc;'
            f'parentScope=;'
            f'shadingMode=useRegistry;'
            f'convertMaterialsTo=[];'
            f'exportInstances=1;'
            f'exportVisibility=1;'
            f'mergeTransformAndShape=1;'
            f'stripNamespaces=1;'
            f'materialsScopeName=mtl" '
            f'-typ "USD Export" -pr -es "{reversed_path}";'
            )
        
        mel.eval(USD_publish_string)
        
        
        cmds.select(clear=True)
   
   
    def openFolder(self):

        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        scene_name_splitted = scene_name.split('_')
        sequence=scene_name_splitted[1]
        shot=scene_name_splitted[2]

        publish_dir=os.path.join(cache_directory,sequence,shot,)
        if not os.path.exists(publish_dir):
            os.makedirs(publish_dir)
        os.startfile(publish_dir)
        print("File explorer opened successfully.")
    
    def publish(self):

        print('-----------------------\n-------DEBUG LOG-------\n-----------------------')
        
        exportList=[]
        for chckBox in self.Chckbox_Names:
            if chckBox.isChecked():
                exportList.append(chckBox.text())
                print(chckBox)
            else:
                pass
        if exportList:
            for asset in exportList:
                publish_file_name, publish_dir = self.get_publish_file_name(asset)
                StartFrame=int(self.lineeditStartFrame.text())
                EndFrame=int(self.lineeditEndFrame.text())
                comment=self.lineeditComment.text()
                publish_file_name=publish_file_name+comment
                fullPathPublish = os.path.join(publish_dir,publish_file_name)
                if not os.path.exists(publish_dir):
                    os.makedirs(publish_dir)
                home_dir = os.path.expanduser("~")
                desktop_path = os.path.join(home_dir, "Desktop")
                fullPathPublishDesktop=(os.path.join(desktop_path,publish_file_name))

                print(f'''
                    -------------------------------
                    exporting {asset}
                    -------------------------------\n
                    __publish file name: {publish_file_name}
                    __Publish Directory: {publish_dir}
                    __full Path Publish: {fullPathPublish}
                    __Start Frame:       {StartFrame}
                    __End Frame:         {EndFrame}
                    ''')
                
                if asset =='shotCam':
                    if not os.path.exists(publish_dir):
                        os.makedirs(publish_dir)
                        print(f"Directory '{publish_dir}' created successfully")
                    self.export_abc(asset,fullPathPublishDesktop,StartFrame,EndFrame)
                    shutil.copyfile(fullPathPublishDesktop+".abc", fullPathPublish+".abc")
                    os.remove(fullPathPublishDesktop+".abc")

                else:
                    self.exportUSD(asset,fullPathPublishDesktop,StartFrame,EndFrame)
                    os.rename(fullPathPublishDesktop+".usd", fullPathPublishDesktop+".usdc")
                    shutil.copyfile(fullPathPublishDesktop+".usdc", fullPathPublish+".usdc")
                    os.remove(fullPathPublishDesktop+".usdc")

        else:
            self.show_error_message("nothing is selected for export")

        
if __name__ == "__main__":

    main_window = mainWindow()
    main_window.show()


