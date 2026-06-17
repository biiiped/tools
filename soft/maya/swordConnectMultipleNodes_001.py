import maya.cmds as cmds

maynode = cmds.ls(sl=1)
nodes=cmds.listRelatives(maynode,ad=1)
value=1

print(nodes)
for node in nodes:

    SR=cmds.createNode("setRange",name=node+"scale")
    cmds.connectAttr(SR+".outValue.outValueY",node+".scaleY")

    #cmds.connectAttr("setRange3.outValue",SR+".input1")

    #cmds.connectAttr("floatConstant1.outFloat",mult+".input2.input2X")
    #cmds.connectAttr("floatConstant1.outFloat",mult+".input2.input2Y")

    cmds.connectAttr("setRange3.outValue.outValueY",SR+".value.valueY")

    cmds.setAttr(SR+".oldMin.oldMinY",0)
    cmds.setAttr(SR+".oldMax.oldMaxY",2)
    cmds.setAttr(SR+".min.minY",-value)
    cmds.setAttr(SR+".max.maxY",value)
    
    value+=1