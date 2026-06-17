import maya.cmds as mc

def  locToGRP():
    
    sel = mc.ls(selection = True)[0]
    children = mc.listRelatives(sel, ad = True)or []

    for c in children:
        if mc.objectType(c, isType = 'locator') == True and mc.attributeQuery("localScaleX",n = c, ex= True )== True:
            mc.delete(c)
            
locToGRP()