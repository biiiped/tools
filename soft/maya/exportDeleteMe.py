import maya.cmds as cmds
import os

def export_selected_to_fbx(file_path):
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("No objects selected. Please select the objects you want to export.")
        return

    cmds.file(file_path, force=True, options="v=0;", typ="Fbx", pr=True,  ea=True)

# Specify the path where you want to save the FBX file
file_path = os.path.join(os.path.expanduser("~"), "Desktop","deleteme.fbx")

# Call the function to export selected objects to FBX
export_selected_to_fbx(file_path)