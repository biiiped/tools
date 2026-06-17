import hou
import os


def create_lpeSub(name,input,output):
    #create subnet, and delete if exist
    lpeSubnetNode = hou.node(f"/stage/{name}")
    if lpeSubnetNode:
        lpeSubnetNode.destroy()
    
    inputPos=input.position()
    lpeSubnetNode=hou.node("/stage/").createNode("subnet",name )
    lpeSubnetNode.move((inputPos[0],inputPos[1]-1))
    lpeSubnetNode.setInput(0, input)
    output.setInput(0, lpeSubnetNode)
    #create the merge
    mergeNode=hou.node(f"/stage/{name}/").createNode("merge", "mergeLpe")
    output=hou.node(f"/stage/{name}/output0")
    output.setInput(0, mergeNode)
    output.move((0,-5))

    return mergeNode


def create_lpe(light,x,y,mergeNode,n):
    path="/stage/lpe_subnetwork/"
    direct_diffuse_lpe=hou.node(path).createNode("rendervar", light+"direct_diffuse_lpe")
    direct_diffuse_lpe.parm("xn__driverparametersaovname_jebkd").set(f"LPE_{light}_direct_diffuse")

    direct_diffuse_lpe.parm("sourceName").set(f"C<RD><L.'LPE_{light}'>.*")

    direct_diffuse_lpe.parm("sourceType").set(f"lpe")
    direct_diffuse_lpe.parm("dataType").set(f"color4f")
    direct_diffuse_lpe.parm("xn__driverparametersaovformat_shbkd").set(f"color4f")
    direct_diffuse_lpe.move((x,y+4))
    direct_diffuse_lpe.setInput(0, hou.node(path).indirectInputs()[0],)
    direct_spec_lpe=hou.node(path).createNode("rendervar", light+"direct_spec_lpe")
    direct_spec_lpe.parm("xn__driverparametersaovname_jebkd").set(f"LPE_{light}_direct_spec")

    direct_spec_lpe.parm("sourceName").set(f"C<RS><L.'LPE_{light}'>.*")

    direct_spec_lpe.parm("sourceType").set(f"lpe")
    direct_spec_lpe.parm("dataType").set(f"color4f")
    direct_spec_lpe.parm("xn__driverparametersaovformat_shbkd").set(f"color4f")
    direct_spec_lpe.setInput(0, direct_diffuse_lpe)
    direct_spec_lpe.move((x,y+2.5))
    mergeNode.setInput(n, direct_spec_lpe)


def create_fxlpe(light,x,y,mergeNode,n):

    path="/stage/fxlpe_subnetwork/"
    direct_diffuse_lpe=hou.node(path).createNode("rendervar", light+"fx_lpe")

    direct_diffuse_lpe.parm("xn__driverparametersaovname_jebkd").set(f"LPE_{light}_fx")
    direct_diffuse_lpe.parm("sourceName").set(f"C.*<L.'LPE_{light}'>.*")

    direct_diffuse_lpe.parm("sourceType").set(f"lpe")
    direct_diffuse_lpe.parm("dataType").set(f"color4f")
    direct_diffuse_lpe.parm("xn__driverparametersaovformat_shbkd").set(f"color4f")
    direct_diffuse_lpe.move((x,y+4))
    direct_diffuse_lpe.setInput(0, hou.node(path).indirectInputs()[0],)
    mergeNode.setInput(n, direct_diffuse_lpe)


def importLPE(input_string):
    light_paths = input_string.split(" ")
    light_list = [path.split("/")[-1] for path in light_paths]

    aovNode=hou.node("/stage/aov")
    nullAovOutput=hou.node("/stage/aov_output")
    mergeNodeLpe=create_lpeSub("lpe_subnetwork",aovNode,nullAovOutput)

    fxaovNode=hou.node("/stage/fx_aov")
    if fxaovNode:
        fxRenderProductNode=hou.node("/stage/fxRenderProduct")
        mergeNodeFxLpe=create_lpeSub("fxlpe_subnetwork",fxaovNode,fxRenderProductNode)

    print(light_list)
    n=0
    for light in light_list:
        create_lpe(light,n*2,0,mergeNodeLpe,n)
        if fxaovNode:
            create_fxlpe(light,n*2,0,mergeNodeFxLpe,n)
        
        n+=1