import maya.cmds as cmds
import maya.mel as mel


def create_null_constraint(bone):
    """
    this function take a bone, and create a null with a constraint to it
    """
    null=cmds.group(em=True, name=bone+"_fix")
    cmds.parentConstraint(bone,null)

    

sl= cmds.ls(sl=True)

for nodes in sl:
    create_null_constraint(nodes)