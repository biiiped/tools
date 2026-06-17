import maya.cmds as cmds
import re

def clean_object_names():
    # Get all objects in the scene
    all_objects = cmds.ls(long=True)

    # Regular expression pattern to match 'FBXACS' followed by three characters
    pattern = re.compile(r'FBXASC\w{3}')

    for obj in all_objects:
        # Extract the short name
        short_name = obj.split('|')[-1]

        # Remove FBX patterns
        new_name = pattern.sub(' ', short_name).strip()

        if new_name != short_name:
            try:
                cmds.rename(obj, new_name)
                print(f'Renamed: {short_name} -> {new_name}')
            except RuntimeError as e:
                print(f'Error renaming {short_name}: {e}')

if __name__ == "__main__":
    clean_object_names()
