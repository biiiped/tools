import os
from pxr import Usd, Kind, UsdGeom

# Default Script
node = hou.pwd()
stage = node.editableStage()



def remove_prim_if_exists(stage, prim_path):
    prim = stage.GetPrimAtPath(prim_path)
    if prim and prim.IsValid():
        stage.RemovePrim(prim_path)
    else:
        print(f"Error: Prim {prim_path} does not exist and cannot be removed.")
        
search_root = "/world/assets/"

def getAssetList(path):
    assetList=[]
    directories = os.listdir(path)
    for typeFolder in directories:
        if typeFolder!="_trash":
            assetFolders=os.listdir(os.path.join(path,typeFolder))
            for assetFolder in assetFolders:
                if assetFolder!="_trash":
                    assetList.append(assetFolder)
    return(assetList)


typeFolderRoot=r"I:\Guerlain_Xmas25\03_Production\Assets"
assets=getAssetList(typeFolderRoot)

assets_in_stage=[]

rule = hou.LopSelectionRule()
rule.setTraversalDemands(hou.lopTraversalDemands.Default)




for asset_name in assets:
    asset_has_over= 0 

    # Create Prim GRP
    prim_path_grp = f"/world/assets/Sets/{asset_name}_GRP"
    new_prim_grp = stage.DefinePrim(prim_path_grp, "Xform")
    Usd.ModelAPI(new_prim_grp).SetKind(Kind.Tokens.group)
    
    #Create the Prim 0
    prim_path_0 = f"/world/assets/Sets/{asset_name}_GRP/{asset_name}_0"
    new_prim_0= stage.DefinePrim(prim_path_0, "Xform")
    
    
    #Prim 0 set transform OP order fix
    Usd.ModelAPI(new_prim_0).SetKind(Kind.Tokens.component)
    inherits = new_prim_0.GetInherits()
    inherits.AddInherit(f"/__class__/{asset_name}")
    transform_list = []
    for attr in new_prim_0.GetAttributes():
        attrName= attr.GetName()
        if attrName.startswith("xformOp:transform:"):
            opSuffix = attrName.split(":")[-1]
            transform_list.append(opSuffix)
    if transform_list:
        xform_prim = UsdGeom.Xformable(new_prim_0)
        for transfrom in transform_list:
            transform_op = xform_prim.AddTransformOp(opSuffix=transfrom)
        asset_has_over= 1

    
            
    # If the asset_has_over is True then create the source primitive else remove the prim
    # I did not find a way to check for over attributs in the stage. a bit dirty...
    if asset_has_over:
        prim_path_source = f"/world/assets/Sets/source/{asset_name}"
        new_prim_source = stage.DefinePrim(prim_path_source, "Xform")
        Usd.ModelAPI(new_prim_source).SetKind(Kind.Tokens.component)
    else:
        remove_prim_if_exists(stage, prim_path_0)
        remove_prim_if_exists(stage, prim_path_grp)