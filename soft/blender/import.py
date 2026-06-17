import bpy

# Replace 'path/to/your/file.fbx' with the actual path to your FBX file
file_path = r'C:\Users\l.bonnaud\Desktop\deleteme.obj'

# Clear existing mesh objects in the scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

# Import FBX file
bpy.ops.import_scene.obj(filepath=file_path)

# Select the imported object
obj = bpy.context.selected_objects[0]

# Set the scale for the object
obj.scale = (0.01, 0.01, 0.01)

# Optionally, you can perform additional operations here after the import
# For example, you can access the imported object like this:
# imported_object = bpy.context.selected_objects[0]

print(f"FBX file '{file_path}' imported successfully.")