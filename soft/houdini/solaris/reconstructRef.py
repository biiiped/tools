import os
import glob

import PrismInit
from pxr import Sdf, Usd, Kind, UsdGeom

     
def get_asset_list():
    """Retrieve a list of asset folders, excluding '_trash' directories."""
    
    root = PrismInit.pcore.getAssetPath()
    
    globpath = os.path.join(root, "*", "*")
    asset_list = glob.glob(globpath)
    
    asset_list = [os.path.basename(asset) for asset in asset_list
                  if not '_trash' in asset]
    
    return asset_list


def replaceReferences(prim, targetPath):
    """Replace prim reference.

    Args:
        prim (pxr.Usd.Prim): Prim to replace reference.
        targetPath (str): Reference path.
    """
     
    references = prim.GetReferences()
    references.ClearReferences()
    prim.GetReferences().SetReferences([])

    if targetPath.lower().endswith(('.usdc', '.usda', '.usd')):
        references.AddReference(targetPath)
    else:
        references.AddInternalReference(Sdf.Path(targetPath))

def get_class_prim_path(prim):
    """Return prim truncated name.

    Args:
        prim (pxr.Usd.Prim): Prim to get name.

    Returns:
        str: Name without number or GRP at the end.
    """    
    
    className = prim.GetName()
    className = className.split('_')[0]
    class_prim_path =rf"/__class__/{className}"
    return class_prim_path


def retrieve_prims_paths(stage, pattern):
    """Retrieve prims from a specified pattern.

    Args:
        stage (pxr.Usd.Stage): USD Stage.
        pattern (str): Search pattern.

    Returns:
        list[str]: List of every prims paths.
    """    
    
    rule = hou.LopSelectionRule()
    rule.setTraversalDemands(hou.lopTraversalDemands.NoDemands)
    rule.setPathPattern(pattern)
    
    return rule.expandedPaths(lopnode=None, stage=stage)


node = hou.pwd()
stage = node.editableStage()
asset_list_network = get_asset_list()

#--  GET PRIMS -- 

search_root = "/world/assets"

#PRIM FOR GRP
pattern_grp = f"{search_root}/Sets/*"
prim_paths_grp = retrieve_prims_paths(stage, pattern_grp)

#PRIM FOR SETS
pattern_set = f"{search_root}/Sets/*/*"
prim_paths_set = retrieve_prims_paths(stage, pattern_set)

#PRIM FOR CHARS
pattern_chars = f"{search_root}/Characters/*"
prim_paths_chars = retrieve_prims_paths(stage, pattern_chars)

#PRIM FOR Props
pattern_props = f"{search_root}/Props/*/* {search_root}/Props/*"
prim_paths_props = retrieve_prims_paths(stage, pattern_props)

#PRIM FOR setDress
pattern_setDress = f"{search_root}/setDress/*/*"
prim_paths_setDress = retrieve_prims_paths(stage, pattern_setDress)

#--  DEFINE PRIMS -- 

# GRP
for prim_path_grp in prim_paths_grp:
    new_prim_grp = stage.DefinePrim(prim_path_grp, "Xform")
    Usd.ModelAPI(new_prim_grp).SetKind(Kind.Tokens.group)
    
    all_children = new_prim_grp.GetAllChildren()
    if not all_children:
        stage.RemovePrim(prim_path_grp)
        continue
        
    asset_name = new_prim_grp.GetName().split("_")[0]
    
    prim_path_0 = f"/world/assets/Sets/{asset_name}_GRP/{asset_name}_0"
    new_prim_0 = stage.DefinePrim(prim_path_0, "Xform")
    
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
            try:
                transform_op = xform_prim.AddTransformOp(opSuffix=transfrom)
            except:
                continue
    
#SET DRESS
for prim_path in prim_paths_setDress:
    prim = stage.GetPrimAtPath(prim_path)
    class_prim_path = get_class_prim_path(prim)
    replaceReferences(prim, class_prim_path)
    
    new_prim_type = stage.DefinePrim(prim_path, "Xform")
    Usd.ModelAPI(new_prim_type).SetKind(Kind.Tokens.component)
    
#SET
for prim_path in prim_paths_set:
    prim = stage.GetPrimAtPath(prim_path)
    class_prim_path = get_class_prim_path(prim)
    replaceReferences(prim, class_prim_path)
    
    new_prim_type = stage.DefinePrim(prim_path, "Xform")
    Usd.ModelAPI(new_prim_type).SetKind(Kind.Tokens.component)
        
#Props
for prim_path in prim_paths_props:
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.GetName() in asset_list_network:
        continue
        
    class_prim_path = get_class_prim_path(prim)
  
    #inherits = prim.GetInherits()
    #inherits.AddInherit(class_prim_path)
    replaceReferences(prim, class_prim_path)
    Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)


#CHARS
for prim_path in prim_paths_chars:
    prim = stage.GetPrimAtPath(prim_path)
    class_prim_path = get_class_prim_path(prim)
    
    inherits = prim.GetInherits()
    inherits.AddInherit(class_prim_path)
    Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)

    
