import maya.cmds as cmds

def calculate_polygon_count(obj):
    # Get the polygon count (faces count) for the object
    poly_count = cmds.polyEvaluate(obj, face=True)
    return poly_count

def list_top_20_polygon_objects():
    # List all polygon objects in the scene
    all_meshes = cmds.ls(type="mesh", long=True)
    if not all_meshes:
        cmds.error("No polygon meshes found in the scene.")
        return
    
    # Get their unique transform nodes (use listRelatives carefully)
    transform_nodes = set()
    for mesh in all_meshes:
        # Get the transform node for each mesh
        transform = cmds.listRelatives(mesh, parent=True, type="transform", fullPath=True)
        if transform:
            transform_nodes.add(transform[0])  # Ensure uniqueness by adding to a set
    
    if not transform_nodes:
        cmds.error("No transform nodes associated with meshes.")
        return
    
    # Calculate polygon count for each object
    polygon_counts = []
    for obj in transform_nodes:
        poly_count = calculate_polygon_count(obj)
        polygon_counts.append((obj, poly_count))
    
    # Sort objects by polygon count in descending order
    polygon_counts.sort(key=lambda x: x[1], reverse=True)
    
    # Get the top 10 polygon count objects
    top_20 = polygon_counts[:20]
    
    # Print the results
    print("Top 10 objects with the highest polygon count in the scene:")
    for rank, (obj, poly_count) in enumerate(top_20, start=1):
        print(f"{rank}. {obj} - Polygon Count: {poly_count}")
    
    return top_20

# Run the function
list_top_20_polygon_objects()
