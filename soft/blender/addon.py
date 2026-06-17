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
        layout.operator("wm.import_fbx_operator", text="in")

        # Button 2
        layout.operator("wm.export_fbx_operator", text="out")

class ImportFBXOperator(bpy.types.Operator):
    bl_idname = "wm.import_fbx_operator"
    bl_label = "Import FBX Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        file_path = r"C:\Users\bonna\Desktop\deleteme.fbx"  # Change this to your OBJ file path
        import_fbx_file(file_path)
        return {'FINISHED'}

class ExportFBXOperator(bpy.types.Operator):
    bl_idname = "wm.export_fbx_operator"
    bl_label = "Export FBX Operator"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        file_path = r"C:\Users\bonna\Desktop\deleteme.fbx"   # Change this to your OBJ file path
        export_fbx_file(file_path)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SimplePanel)
    bpy.utils.register_class(ImportFBXOperator)
    bpy.utils.register_class(ExportFBXOperator)

def unregister():
    bpy.utils.unregister_class(SimplePanel)
    bpy.utils.unregister_class(ImportFBXOperator)
    bpy.utils.unregister_class(ExportFBXOperator)

def import_fbx_file(file_path):
    # Clear existing mesh objects in the scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Import FBX file
    bpy.ops.import_scene.fbx(
        filepath=file_path,
        global_scale =100
    )


    print(f"FBX file '{file_path}' imported successfully.")

def export_fbx_file(file_path):
    # Get the selected objects in the scene
    selected_objects = bpy.context.selected_objects

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
        bpy.ops.export_scene.fbx(
            filepath=file_path,
            use_selection=True,
            global_scale =0.01
        )

        print(f"Exported selected objects to: {file_path}")
    else:
        print("No objects selected. Please select objects to export.")

if __name__ == "__main__":
    register()
