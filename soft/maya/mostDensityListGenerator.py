import maya.cmds as cmds

def calculate_density(obj):
    
    # Get the vertex count
    vertex_count = cmds.polyEvaluate(obj, vertex=True)
    # Get the surface area
    surface_area = cmds.polyEvaluate(obj, area=True)
    # Avoid division by zero
    density = vertex_count / surface_area if surface_area > 0 else 0
    return density

def list_top_10_dense_objects():
    # List all polygon objects in the scene
    all_meshes = cmds.ls(type="mesh", long=True)
    if not all_meshes:
        cmds.error("No polygon meshes found in the scene.")
        return
    
    # Get their unique transform nodes (use listRelatives carefully)
    transform_nodes = set()
    for mesh in all_meshes:
        # Get the transform node for each mesh
        transform = cmds.listRelatives(mesh, parent=True, type="transform",fullPath=True)
        if transform:
            transform_nodes.add(transform[0])  # Ensure uniqueness by adding to a set
            
    
    if not transform_nodes:
        cmds.error("No transform nodes associated with meshes.")
        return
    
    # Calculate density for each object
    densities = []
    for obj in transform_nodes:
        
        density = calculate_density(obj)
        densities.append((obj, density))
    
    # Sort objects by density in descending order
    densities.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top 10 densest objects
    top_10 = densities[:10]
    
    # Print the results
    print("Top 10 densest objects in the scene:")
    for rank, (obj, density) in enumerate(top_10, start=1):
        print(f"{rank}. {obj} - Density: {density:.2f}")
    
    return top_10

# Run the function
list_top_10_dense_objects()
