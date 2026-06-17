import maya.cmds as cmds
import os

def export_selected_to_fbx(file_path):
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("No objects selected. Please select the objects you want to export.")
        return

    cmds.file(file_path, force=True,options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", type="Fbx", exportSelected =True)

# Specify the path where you want to save the FBX file
name=cmds.ls(sl=1)
file_path = r"\\MINERVA\3d4_23_24\MECHA\09_publish\asset\03_item\geo"
file_name = f"MCH_itm_{name[0]}_geo_P.fbx"
full_path =os.path.join(file_path,file_name)
print(full_path)

# Call the function to export selected objects to FBX
export_selected_to_fbx(full_path)