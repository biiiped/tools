import maya.cmds as cmds


def connect_selected_attributes(outNode,inNode,attrout,attrin):
    source_attr = f"{outNode}.{attrout}"
    target_attr = f"{inNode}.{attrin}"
    cmds.connectAttr(source_attr, target_attr, force=True)
    
selected_nodes = cmds.ls(selection=True)
    
if len(selected_nodes) < 2:
    cmds.warning("Please select two nodes: the source and then the target.")

outNode = selected_nodes[0]
selected_nodes.pop(0)
inNode = selected_nodes[1]
attrIn="rotate"
attrOut="outColor"
for node in selected_nodes:
    print(f"connecting {outNode} {attrOut} and {node} {attrIn}")
    connect_selected_attributes(outNode,node,attrOut,attrIn)
    