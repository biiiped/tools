import maya.cmds as cmds

def merge_group():
    # Get the selected group
    selected = cmds.ls(selection=True, long=True)
    
    if not selected or len(selected) != 1:
        cmds.error("Please select a single group.")
        return

    group = selected[0]
    print(f"group = {group}")
    # Check if the selection is a group
    children = cmds.listRelatives(group, children=True, fullPath=True)
    print(f"children = {children}")
    if not children:
        cmds.error("The selected group has no children to merge.")
        return

    # Combine all children of the group
    merged_object = cmds.polyUnite(children, mergeUVSets=True, constructionHistory=True)[0]
    merged_object = cmds.rename(merged_object, group.split('|')[-1])
    print(f"merged_object = {merged_object}")
    # Re-parent the merged object to the group
    
    cmds.parent(merged_object, group)

    # Clean up: Delete original children
    cmds.delete(children)
    cmds.delete(selection, ch=True)
    print(f"Merged objects in group '{group}' into a single object '{merged_object}'.")

# Run the function
merge_group()
