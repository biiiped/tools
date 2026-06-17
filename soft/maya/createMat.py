import maya.cmds as cmds

def create_and_assign_shader():
    # Get the list of selected objects
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.warning("No objects selected. Please select at least one object.")
        return
    
    for obj in selected_objects:
        # Create a new Blinn shader
        shader_name = 'mat_' + obj
        shader = cmds.shadingNode('blinn', asShader=True, name=shader_name)
        
        # Create a shading group for the shader
        shading_group = cmds.sets(shader, renderable=True, noSurfaceShader=True, empty=True, name=shader_name + 'SG')
        
        # Connect the shader to the shading group
        cmds.select(obj)
        cmds.hyperShade(assign=shader_name)
        
        # Assign the shader to the object
        cmds.select(obj)
        cmds.hyperShade(assign=shader_name)
        
    print(f"Shaders assigned to selected objects: {', '.join(selected_objects)}")

# Call the function
create_and_assign_shader()