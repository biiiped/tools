import maya.cmds as cmds
import os
import re

project_name = 'MECHA'
lil_project_name = 'MCH'

def archive_old_publish(file_path):
    directory_path = os.path.dirname(file_path)
    full_file_name=os.path.basename(file_path)
    file_name, extension = os.path.splitext(full_file_name)
    old_path=os.path.join(directory_path,"old")
    
    max_increment = 0
    target_file = None
    
    #first, we create old if it don't exist
    if not os.path.exists(old_path):
        os.makedirs(old_path)
        print(f"Folder '{old_path}' created.i create it")
    else:
        print(f"Folder '{old_path}' already exists. i don't create it")
    
    old_files = os.listdir(old_path)


    # check if there file with bad name
    pattern = re.compile(r'_\d{3}\.')
    # Check if each filename matches the pattern
    for old_file_name in old_files:
        match = pattern.search(old_file_name)
        if match:
            pass
        else:
            print(f"{old_file_name} does not have an increment ")

    
    for old_file_name in old_files:
        if old_file_name.startswith(file_name):
            print(f"old_file found ! : {old_file_name}")
            # Extract numeric increment from the old_file_name
            try:
                increment = int(old_file_name[len(file_name) + 1:-4])  # Extracting the numeric part and removing '.fbx'
                if increment > max_increment:
                    max_increment = increment
                    target_file = old_file_name
                    print(f"old_file with the biggest increment is {target_file} !")
            except ValueError:
                pass  # Ignore old_file_name that don't have a valid numeric increment
                print("error")
        else :
            print(f"{file_name} does not have an increment ")

    if target_file:
        print(f"The file with the largest increment is: {target_file}")
        print(f"The max increment is: {max_increment}")
    else:
        print("No matching files found.the increment is 1")
    
    
    increment = "{:03d}".format(max_increment+1)
    new_full_filename=f"{file_name}_{increment}{extension}"

    try:
        # Duplicate the file
        with open(file_path, 'rb') as source_file:
            with open(os.path.join(old_path, new_full_filename), 'wb') as dest_file:
                dest_file.write(source_file.read())

        print(f"File duplicated successfully to {old_path}")

    except Exception as e:
        print(f"Error: {e}")

def export_selected_to_fbx(file_path):
    print("export_selected_to_fbx")
    selected_objects = cmds.ls(selection=True, long=True)
    
    if not selected_objects:
        cmds.warning("No objects selected. Please select the objects you want to export.")
        return
    cmds.file(file_path, force=True, options="v=0;", typ="Fbx", pr=True,  ea=True)


print("")
print("-------------------")
publish_directory = f"//MINERVA/3d4_23_24/{project_name}/09_publish/asset"
print(f"publish_directory:{publish_directory}")
print("")

current_file_path = cmds.file(q=True, sceneName=True)
print(f"current_file_path:{current_file_path}")

directory_path = os.path.dirname(current_file_path)
print(f"directory_path:{directory_path}")

current_file_name=os.path.basename(current_file_path)
print(f"current_file_name:{current_file_name}")
print("")

# Split the file name using underscores
file_name_parts = current_file_name.split('_')

shortType = file_name_parts[1]
print(f"shortType:{shortType}")

name = file_name_parts[2]
print(f"name:{name}")

# Use a different variable name instead of 'type'
asset_type = ""

if shortType == "chr":
    asset_type = "01_character"
elif shortType == "prp":
    asset_type = "02_prop"
elif shortType == "itm":
    asset_type = "03_item"
elif shortType == 'mod':
    asset_type = "05_module"
elif shortType == "env":
    asset_type = "04_enviro"

print(f"asset_type:{asset_type}")
print("")

publish_file = f"{lil_project_name}_{shortType}_{name}_geo_P.fbx"
print(f"publish_file:{publish_file}")

publish_path = os.path.join(publish_directory, asset_type, "geo", publish_file)
publish_path = publish_path.replace('\\', '/')
print(f"publish_path:{publish_path}")
print("")


if os.path.exists(publish_path):
    print("there is already a publish, i archive it")
    archive_old_publish(publish_path)


export_selected_to_fbx(publish_path)
