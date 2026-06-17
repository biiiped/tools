import maya.cmds as cmds
nodeList=[]
x = 1
selected_nodes = cmds.ls(selection=True)
for node in selected_nodes:
    node_name = node.split(':')[-1]
    nodeList.append(node_name)

enum_string = ':'.join(nodeList)
cmds.addAttr("master_CTL", longName="diamond", attributeType='enum', enumName=enum_string, keyable=True)

for node in selected_nodes:
    node_name = node.split(':')[-1]
    condition_node_name = node_name + "_diamond_condition"
    condition_node = cmds.shadingNode('condition', asUtility=True, name=condition_node_name)
    cmds.setAttr(condition_node + ".secondTerm", x)
    cmds.setAttr(condition_node + ".operation", 0)
    cmds.setAttr(condition_node + ".colorIfTrue.colorIfTrueR", 1)
    cmds.setAttr(condition_node + ".colorIfFalse.colorIfFalseR", 0)
    cmds.connectAttr('master_CTL.diamond', condition_node + ".firstTerm", force=True)
    cmds.connectAttr(condition_node + ".outColorR", node + ".visibility", force=True)
    x += 1