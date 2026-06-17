import maya.cmds as cmds

offset=30


def move_selected_nodes():
    selected_nodes = cmds.ls(selection=True)
    if not selected_nodes:
        cmds.warning("No nodes selected.")
        return
    x=0
    for node in selected_nodes:
        cmds.xform(node, translation=(x*offset, 0, 0), relative=True)
        x+=1
move_selected_nodes()