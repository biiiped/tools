from pxr import Usd, Sdf


def replaceReferences(prim,targetPath):
    references = prim.GetReferences()
    references.ClearReferences()
    prim.GetReferences().SetReferences([])
    if targetPath.lower().endswith(('.usdc', '.usda', '.usd')):
        references.AddReference(targetPath)
    else:
        references.AddInternalReference(Sdf.Path(targetPath))

node = hou.pwd()
ls = hou.LopSelectionRule()
ls.setPathPattern('LayoutRight/*')
paths = ls.expandedPaths(node.inputs()[0])
stage = node.editableStage()
targetPath=r"I:\Guerlain_Xmas25\03_Production\Assets\Characters\butterfly\Export\USD\v0001\butterfly_USD_v0001.usda"

for path in paths:
    prim = stage.GetPrimAtPath(path)
    replaceReferences(prim,targetPath)

