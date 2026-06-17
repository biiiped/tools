import maya.cmds as cmds
import time

def create_and_delete_bs(mesh1, mesh2,pageNumber):
    if not (cmds.objExists(mesh1) and cmds.objExists(mesh2)):
        print("One or both meshes do not exist.")

    ratiio=1.0/pageNumber
    ratiioCount=0.0
    bs_node = cmds.blendShape(mesh2, mesh1, name="tempBlendShape")[0]
    print(f"BlendShape created: {bs_node}")

    for page in range(1, pageNumber + 1):
        ratiioCount+=ratiio
        
        cmds.setAttr(f"{bs_node}.{mesh2}", ratiioCount)
        newPage=cmds.duplicate(mesh1, name=f"page_{page}")
        print(f"BlendShape weight set to {ratiioCount}")

    cmds.delete(bs_node)

pageNumber=100
create_and_delete_bs('urf_1', 'urf_100', pageNumber)


