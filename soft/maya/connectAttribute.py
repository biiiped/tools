import maya.cmds as cmds

def connect_selected_attributes(attrout,attrin):
    # Get the selected nodes
    selected_nodes = cmds.ls(selection=True)
    
    if len(selected_nodes) < 2:
        cmds.warning("Please select two nodes: the source and then the target.")
        return
    
    # Get the source and target nodes
    source_node = selected_nodes[0]
    target_node = selected_nodes[1]
    
    
    source_attr = f"{source_node}.{attrout}"
    target_attr = f"{target_node}.{attrin}"
    cmds.connectAttr(source_attr, target_attr, force=True)
    
connect_selected_attributes("scale","scale")
