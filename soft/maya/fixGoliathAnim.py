import maya.cmds as cmds

cmds.cutKey( 'pSphere1', attribute='translateX', option="curve" )
print("copied")
cmds.pasteKey( 'pSphere1', time=(1,1), attribute='translateX' )
