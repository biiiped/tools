import maya.cmds as cmds
import maya.mel as mel


def replace_ctl(ctrl,bone):
    """this function take a ctrl then a bone
    
    it will replace the shape of the bone to the shape 
    of the ctrl while respecting all the transform of
    the two node"""
    boneShape=cmds.listRelatives(bone,s=1)
    if boneShape:
        print("deleting boneShape")
        cmds.delete(boneShape,s=1)
    ctrlParent = cmds.listRelatives(ctrl, parent=True)
    if ctrlParent:
        #si le controller a un parent, parente le controler a world
        cmds.parent(ctrl,w=1)
    cmds.makeIdentity(bone,apply=1,scale=1)
    cmds.select(ctrl,bone)
    mel.eval("matchTransform -piv; matchPivotOrient;")
    cmds.move(0,0,0,ctrl,rpr=1)
    cmds.makeIdentity(ctrl,apply=1,t=1,scale=1)
    
    ctrlShape=cmds.listRelatives(ctrl,s=1)
    ctrlShape=cmds.rename(ctrlShape,bone+'_shape')
    cmds.parent(ctrlShape,bone,s=1,r=1)
    cmds.delete(ctrl)

sl= cmds.ls(sl=True)
bone=sl[1]
ctrl=sl[0]
replace_ctl(ctrl,bone)
