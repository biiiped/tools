import maya.cmds as cmds
import maya.mel as mel

"""ce script prends un hierarchie de joint et créé sa hierarchie de controllers"""

def createCtlFromJntHierarchy(rootJnt,radius):
    all_decendent=cmds.listRelatives(rootJnt,ad=1)
    jntHierachy=all_decendent+[rootJnt]
    for joint in jntHierachy:
        ctrlName="fkCtl_"+joint
        ctl=cmds.circle(n=ctrlName,r=radius)
        cmds.rotate(0,90,0)
        cmds.makeIdentity(apply=1)
        cmds.matchTransform(ctl,joint)
    cmds.select(cl=True)