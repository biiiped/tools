import maya.cmds as cmds

def rename_shading_groups():
    shading_groups = cmds.ls(type="shadingEngine")
    for sg in shading_groups:
        # Find the connected material
        connected_mat = cmds.listConnections(sg + ".surfaceShader", source=True, destination=False)
        if connected_mat:
            mat_name = connected_mat[0]
            new_sg_name = mat_name + "_mat"
            # Rename the shading group
            try:
                cmds.rename(sg, new_sg_name)
                print(f"Renamed {sg} to {new_sg_name}")
            except RuntimeError as e:
                print(f"Could not rename {sg}: {e}")

rename_shading_groups()
