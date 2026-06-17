import maya.cmds as cmds

def count_objects_in_selection():
    # Get the selected object
    selection = cmds.ls(selection=True)
    
    if not selection:
        cmds.error("Please select an object.")
        return
    
    # Get all descendants of the selected object
    descendants = cmds.listRelatives(selection[0], allDescendents=True, type="transform") or []
    
    # Include the selected object itself in the count
    total_count = len(descendants) + 1
    
    print(f"Total objects in {selection[0]}: {total_count}")
    return total_count

# Run the function
count_objects_in_selection()
