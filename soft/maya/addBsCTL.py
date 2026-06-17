import maya.cmds as cmds

def add_blendshape_controls():
    selection = cmds.ls(selection=True)
    
    if len(selection) != 2:
        cmds.warning("Please select exactly two objects.")
        return
    
    source_obj, target_obj = selection
    
    # Find the blendShape node connected to the first object
    blendshape_nodes = cmds.ls(cmds.listHistory(source_obj), type='blendShape')
    
    if not blendshape_nodes:
        cmds.warning("No blendShape node found on the first selected object.")
        return
    
    blendshape_node = blendshape_nodes[0]
    
    # Get blendShape targets
    targets = cmds.aliasAttr(blendshape_node, query=True)
    
    if not targets:
        cmds.warning("No blendShape targets found.")
        return
    
    for i in range(0, len(targets), 2):  # aliasAttr returns name/index pairs
        target_name = targets[i]
        attr_name = target_name.replace(" ", "_")
        full_attr_name = f"{target_obj}.{attr_name}"
        
        if not cmds.attributeQuery(attr_name, node=target_obj, exists=True):
            cmds.addAttr(target_obj, longName=attr_name, attributeType='float', min=0, max=10, defaultValue=0, keyable=True)
        
        # Connect the attribute to the blendShape weight
        cmds.connectAttr(full_attr_name, f"{blendshape_node}.{target_name}", force=True)
    
    
add_blendshape_controls()
