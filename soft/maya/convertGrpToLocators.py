import maya.cmds as cmds


selected_objects = cmds.ls(selection=True)

loc=[]
for obj in selected_objects:
    position = cmds.xform(obj, query=True, worldSpace=True, translation=True)
    locator = cmds.spaceLocator()[0]
    cmds.xform(locator, worldSpace=True, translation=position)
    cmds.parent(locator,obj)
    cmds.parent(locator,obj)
    loc.append(locator)
cmds.select(clear=True)
cmds.select(loc)

print("Locators created for selected geometries.")
