import maya.cmds as cmds
import os

def import_obj(obj_path):
    # Check if the file exists
    if not cmds.file(obj_path, q=True, exists=True):
        print(f"File not found: {obj_path}")
        return

    # Import the OBJ file
    imported_objects = cmds.file(obj_path, i=True, type="FBX", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace="")

            

# Replace this path with the actual path to your OBJ file
file_path = os.path.join(os.path.expanduser("~"), "Desktop","deleteme.fbx")


# Call the function to import the scaled OBJ file
import_obj(file_path)
