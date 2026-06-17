import bpy
import mathutils

def create_cubes_for_bones():
    obj = bpy.context.object
    
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature.")
        return
    
    armature = obj
    
    for bone in armature.data.bones:
        cube_name = f"{bone.name}_ctrl"
        existing_cube = bpy.data.objects.get(cube_name)
        
        if existing_cube:
            # Check if it already has the correct constraint
            for constraint in existing_cube.constraints:
                if constraint.type == 'CHILD_OF' and constraint.target == armature and constraint.subtarget == bone.name:
                    print(f"{cube_name} already set up.")
                    continue
            
            # Rename existing cube if necessary
            new_name = f"{cube_name}_old"
            counter = 1
            while bpy.data.objects.get(new_name):
                new_name = f"{cube_name}_old_{counter}"
                counter += 1
            
            existing_cube.name = new_name
            print(f"Renamed existing cube to {new_name}.")
        
        # Create a new cube
        bpy.ops.mesh.primitive_cube_add(size=0.1)
        cube = bpy.context.object
        cube.name = cube_name
        
        # Match cube location and orientation to bone
        bone_matrix = armature.matrix_world @ bone.matrix_local
        cube.matrix_world = bone_matrix
        
        # Add constraint
        constraint = cube.constraints.new(type='CHILD_OF')
        constraint.target = armature
        constraint.subtarget = bone.name
        
        print(f"Created cube {cube_name} and assigned Child Of constraint to {bone.name}.")

# Run the function
create_cubes_for_bones()
