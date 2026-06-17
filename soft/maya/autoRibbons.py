import maya.cmds as cmds

#select two joint , a ribbon, and it will make all the constraint
def attachRibbons(jnt1,jnt2,ribbon):
    ribbonNum=ribbon.split("_")[1]
    generalCtl="CTL_GeneralRibbon_"+ribbonNum
    ACtl="CTL_Ribbon_A_"+ribbonNum
    BCtl="CTL_Ribbon_B_"+ribbonNum

    cmds.parentConstraint(jnt1,jnt2,generalCtl,mo=0,sr=['x','y','z'])
    
    cmds.orientConstraint(jnt1,generalCtl,mo=0)
    cmds.pointConstraint(jnt1,ACtl,mo=0)
    cmds.pointConstraint(jnt2,BCtl,mo=0)
    cmds.matchTransform(ACtl,jnt1,rot=1)
    cmds.matchTransform(BCtl,ACtl,rot=1)

    cmds.parent("ExtraNodes_"+ribbonNum,'XtraRibbon')
    cmds.parent(generalCtl,'ribbonCtl')

    generalShp=cmds.listRelatives(generalCtl,shapes=1)
    cmds.hide(generalShp)

def rotateRibbon(ribbonNum,rotate,axe):
    current_rotation = cmds.getAttr("CTL_Ribbon_A_"+ribbonNum+ ".rotate"+axe)
    cmds.setAttr("CTL_Ribbon_A_"+ribbonNum+ ".rotate"+axe, current_rotation+rotate)
    current_rotation = cmds.getAttr("CTL_Ribbon_B_"+ribbonNum+ ".rotate"+axe)
    cmds.setAttr("CTL_Ribbon_B_"+ribbonNum+ ".rotate"+axe, current_rotation+rotate)

#for i in range(8):
#    cmds.file(r"C:\Users\bonna\Desktop\Ribbon_Matrice.ma",i=True,uns=0)


attachRibbons('bind_ikJnt_leg_L','bind_ikJnt_knee_L','Ribbon_01')
attachRibbons('bind_ikJnt_knee_L','ikJnt_ankle_L','Ribbon_02')
attachRibbons('bind_ikJnt_leg_R','bind_ikJnt_knee_R','Ribbon_03')
attachRibbons('bind_ikJnt_knee_R','ikJnt_ankle_R','Ribbon_04')
attachRibbons('bind_ikJnt_shoulder_L','bind_ikJnt_elbow_L','Ribbon_05')

attachRibbons('bind_ikJnt_elbow_L','ikJnt_wrist_L','Ribbon_06')

attachRibbons('bind_ikJnt_shoulder_R','bind_ikJnt_elbow_R','Ribbon_07')

attachRibbons('bind_ikJnt_elbow_R','ikJnt_wrist_R','Ribbon_08')
rotateRibbon("05",90,"X")
rotateRibbon("07",90,"X")

