import bpy

class SimplePanel(bpy.types.Panel):
    bl_label = "Simple Panel"
    bl_idname = "PT_SimplePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout

        # Button 1
        layout.operator("wm.import_obj_operator", text="in")

        # Button 2
        layout.operator("wm.export_obj_operator", text="out")

class ImportOBJOperator(bpy.types.Operator):
    bl_idname = "wm.import_obj_operator"
    bl_label = "Import OBJ Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        file_path = r'C:\Users\l.bonnaud\Desktop\deleteme.obj'  # Change this to your OBJ file path
        import_obj_file(file_path)
        return {'FINISHED'}

class ExportOBJOperator(bpy.types.Operator):
    bl_idname = "wm.export_obj_operator"
    bl_label = "Export OBJ Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        file_path = r'C:\Users\l.bonnaud\Desktop\deleteme.obj'  # Change this to your OBJ file path
        export_obj_file(file_path)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SimplePanel)
    bpy.utils.register_class(ImportOBJOperator)
    bpy.utils.register_class(ExportOBJOperator)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(ImportOBJOperator)
    bpy.utils.unregister_class(ExportOBJOperator)

def import_obj_file(file_path):
    # Clear existing mesh objects in the scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Import OBJ file
    bpy.ops.import_scene.obj(filepath=file_path)

    # Select the imported object
    obj = bpy.context.selected_objects[0]

    # Set the scale for the object
    obj.scale = (1, 1, 1)

    print(f"OBJ file '{file_path}' imported successfully.")

def export_obj_file(file_path):
    # Get the selected objects in the scene
    selected_objects = bpy.context.selected_objects
    scale_factor = 0.01

    # Check if there are any selected objects
    if selected_objects:
        # Select all objects to be exported
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)

        # Set the context to OBJECT mode
        bpy.context.view_layer.objects.active = bpy.context.view_layer.objects[selected_objects[0].name]
        bpy.ops.object.mode_set(mode='OBJECT')

        # Export the selected objects as OBJ
        bpy.ops.export_scene.obj(
            filepath=file_path,
            use_selection=True,
            use_materials=True,
            global_scale =scale_factor
        )

        print(f"Exported selected objects to: {file_path}")
    else:
        print("No objects selected. Please select objects to export.")

if __name__ == "__main__":
    register()
