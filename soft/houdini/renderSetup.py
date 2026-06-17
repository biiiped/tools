import os
import hou
import json
import re


publishShotPath=r"\\MINERVA\3d4_23_24\MECHA\09_publish\shot"
renderLayersList=[]
renderLayersDict = {}

shotNum=1

color_dict = {
    "all": (1,0,1),
    "bg": (1,0,1),
    "mg": (1,0,1),
    "fg": (1,0,1),
    "shark": (1,0,1),
    "goliath": (1,0,1),
    "rick": (1,0,1),
    "zeke": (1,0,1),
    "crypto": (1,0,1),
    "fog": (1,0,1),
    "fx": (1,0,1)
}

def get_emplacement(shot_key):
    with open(r"\\MINERVA\3d4_23_24\MECHA\02_ressource\@LOUIS\ressources\thumbnail\timeRanges.json", 'r') as file:
        data = json.load(file)
    # Extract the sequence from the shot key
    sequence_prefix = "_".join(shot_key.split("_")[:-1])
    
    # Collect all keys for this sequence and sort them
    sequence_keys = sorted([key for key in data.keys() if key.startswith(sequence_prefix)])
    
    # Find the index (1-based) of the given shot key in the sorted sequence keys
    if shot_key in sequence_keys:
        return sequence_keys.index(shot_key) + 1
    else:
        return None  # The shot key doesn't exist in the data

def getLastShotVersion(seqID, shID):
    path1 = f"//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render/{seqID}/{shID}"
    try:
        items = os.listdir(path1)
        # Get directories that match the pattern 'v' followed by a number
        version_pattern = re.compile(r"^v(\d+)$")
        versions = [item for item in items if os.path.isdir(os.path.join(path1, item)) and version_pattern.match(item)]
        
        # Extract the numeric part and convert it to an integer
        version_numbers = [int(version_pattern.match(v).group(1)) for v in versions]
        
        # If there are no versions, return 'v1'
        if not version_numbers:
            return "v1"
        
        # Find the maximum existing version number and increment it
        max_version = max(version_numbers)
        new_version = f"v{max_version + 1}"
        
        return new_version
    except Exception as e:
        print(e)
        return "v1"

def getFrameRange(shotName):
    with open(r"\\MINERVA\3d4_23_24\MECHA\02_ressource\@LOUIS\ressources\thumbnail\timeRanges.json", 'r') as file:
        data = json.load(file)
    if shotName in data:
        values = data[shotName]
        
        return (values)
        
    return (1000,1100)

def find_render_layers(start_path):

    for root, dirs, files in os.walk(start_path):

        if "renderLayer" in dirs:
            render_layer_path = os.path.join(root, "renderLayer")
            for fileRoot, fileDirs, fileFiles in os.walk(render_layer_path):
                renderLayersList.append(fileFiles)

    for sublist in renderLayersList:
        if sublist:
            parts = sublist[0].split('_')
            key = f"{parts[1]}_{parts[2]}"
            renderLayersDict[key] = sublist

    return renderLayersDict


def create_sublayer(sublayerName,seqID,shID,layerID,x,y):
    lopPath = hou.node(f'/stage/sub_{seqID}')
    sublayerNode = lopPath.createNode('sublayer', sublayerName)
    RenderLayerFilePath=f"//MINERVA/3d4_23_24/MECHA/09_publish/shot/{seqID}/{shID}/renderLayer/MCH_{seqID}_{shID}_{layerID}_P.usdc"
    sublayerNode.parm('filepath1').set(RenderLayerFilePath)
    sublayerNode.move((x,y))
    return sublayerNode

    
def create_nullout(nulloutName,seqID,shID,layerID,x,y,sublayerNode):
    lopPath = hou.node(f'/stage/sub_{seqID}')
    null = lopPath.createNode('null', nulloutName)
    null.move((x,y))
    null.setInput(0, sublayerNode)


def create_usdRender(usdRenderName,seqID,shID,layerID,x,y):

    
    ropPath = hou.node(f'/stage/rop_{seqID}')
    usdRenderNode = ropPath.createNode('usdrender', usdRenderName)
    
    usdRenderNode.parm('trange').set(f'normal')
    expressionX = f'ch("../{shID}/frameRangex")'.format(shID)
    expressionY = f'ch("../{shID}/frameRangey")'.format(shID)
    expressionZ = f'ch("../{shID}/frameStep")'.format(shID)
    usdRenderNode.parm('f1').setExpression(expressionX)
    usdRenderNode.parm('f2').setExpression(expressionY)
    usdRenderNode.parm('f3').setExpression(expressionZ)
    usdRenderNode.parm('renderer').set("HdArnoldRendererPlugin")
    usdRenderNode.parm('loppath').set(f'/stage/sub_`{seqID}/{seqID}_{shID}_{layerID}_nullout')
    usdRenderNode.parm('rendersettings').set("/Render/rendersettings")
    usdRenderNode.parm('outputimage').set(f'`chs("../{shID}/renderDir")`/{layerID}/{seqID}_{shID}_{layerID}_aov_`chs("../{shID}/version")`_<F4>.exr')
    usdRenderNode.parm('override_res').set('scale')
    expression3=f'ch("../{shID}/resolution")'.format(shID)
    usdRenderNode.parm('res_scale').setExpression(expression3)
    usdRenderNode.parm('alfprogress').set(0)
    usdRenderNode.parm('husk_mplay').set(1)
    
    usdRenderNode.move((x,y))
    
    if layerID=="cryptomatte":
        usdRenderNode.bypass(True)

    return usdRenderNode


def create_controlMerge(controlMergeName,seqID,shID,x,y):

    lastShotVersion=getLastShotVersion(seqID,shID)
    frameRange=getFrameRange(seqID+"_"+shID)

    ropPath = hou.node(f'/stage/rop_{seqID}')
    controlMergeNode = ropPath.createNode('merge', controlMergeName)
    
    parm_group = controlMergeNode.parmTemplateGroup()
    
    mainRenderDir_parm_name = 'mainRenderDir'
    mainRenderDir_parm_label = 'mainRender directory'
    mainRenderDir_parm_default = "//MINERVA/3d4_23_24/MECHA/08_editing/input/05_render"
    mainRenderDir_parm_template = hou.StringParmTemplate(mainRenderDir_parm_name, mainRenderDir_parm_label, 1, default_value=(mainRenderDir_parm_default,))
    parm_group.append(mainRenderDir_parm_template)
    
    renderDir_parm_name = 'renderDir'
    renderDir_parm_label = 'render directory'
    renderDir_parm_default = f'`chs("mainRenderDir")`/{seqID}/{shID}/`chs("version")`'
    renderDir_parm_template = hou.StringParmTemplate(renderDir_parm_name, renderDir_parm_label, 1, default_value=(renderDir_parm_default,))
    parm_group.append(renderDir_parm_template)
    
    version_parm_name = 'version'
    version_parm_label = 'version'
    version_parm_default = lastShotVersion
    version_parm_template = hou.StringParmTemplate(version_parm_name, version_parm_label, 1, default_value=(version_parm_default,))
    parm_group.append(version_parm_template)
    
    frameRange_parm_name = 'frameRange'
    frameRange_parm_label = 'frame range'
    frameRange_parm_default = frameRange
    frameRange_parm_template = hou.IntParmTemplate(frameRange_parm_name, frameRange_parm_label,2, default_value=frameRange_parm_default)
    parm_group.append(frameRange_parm_template)
    
    resolution_parm_name = 'resolution'
    resolution_parm_label = 'resolution'
    resolution_parm_default = (100,)
    resolution_parm_template = hou.IntParmTemplate(resolution_parm_name, resolution_parm_label,1, default_value=(resolution_parm_default),min=1,max=100)
    parm_group.append(resolution_parm_template)
    
    frameStep_parm_name = 'frameStep'
    frameStep_parm_label = 'frame step'
    frameStep_parm_default = (1,)
    frameStep_parm_template = hou.IntParmTemplate(frameStep_parm_name, frameStep_parm_label,1, default_value=frameStep_parm_default,min=1,max=500)
    parm_group.append(frameStep_parm_template)
    
    controlMergeNode.setParmTemplateGroup(parm_group)
    
    controlMergeNode.move((x,y))

    return controlMergeNode


def create_shot(shot,shotPosx,shotPosy):
    n=1
    ratio=5
    
    parts = shot.split('_')
    shID=parts[1]
    seqID=parts[0]
    


    controlMergeName=shID
    controlMergeNode=create_controlMerge(controlMergeName,seqID,shID,shotPosx+0.3,shotPosy+0.3)

    networksub = hou.node(f"/stage/sub_{seqID}")
    networkrop = hou.node(f"/stage/rop_{seqID}")
    networks=[networksub,networkrop]
    for net in networks:
        backdrop = net.createNetworkBox()
        backdrop.setPosition((shotPosx, shotPosy))
        backdrop.setSize((60, 2.5))
        backdrop.setColor(hou.Color(0.5, 0.7, 1.0))
        backdrop.setComment(f"Backdrop {shID}")
    
    shotRendeLayers=renderLayersDict[shot]
    for renderLayer in shotRendeLayers:
        color=(0,0,0) 
        parts = renderLayer.split('_')
        layerID=parts[3]
        renderLayerToken=shot+"_"+layerID
        
        sublayerName=renderLayerToken+"_sublayer"
        sublayerNode=create_sublayer(sublayerName,seqID,shID,layerID,shotPosx+n*ratio-4,shotPosy+1.5)
        
        nulloutName=renderLayerToken+"_nullout"
        create_nullout(nulloutName,seqID,shID,layerID,shotPosx+n*ratio-5,shotPosy+0.5,sublayerNode)
        
        lastShotVersion=getLastShotVersion(seqID,shID)
        usdRenderName=renderLayerToken+"_usdrender_"+lastShotVersion
        
        usdRenderNode=create_usdRender(usdRenderName,seqID,shID,layerID,shotPosx+n*ratio,shotPosy+1.5)
        
        controlMergeNode.setInput(n, usdRenderNode)
        
        n+=1

root=hou.node('/stage')
for network in root.children():
    try:
        network_boxes = network.networkBoxes()
        for box in network_boxes:
            box.destroy()
    except Exception as e:
        print(e)
for network in root.children():
    for child in network.children():
        if child.name() != "deadline1":
            if child.name() != "updateThumb":
                child.destroy()

renderLayersDict=find_render_layers(publishShotPath)

for key, value in renderLayersDict.items():
            print(key)
            print(value)
            print("")

for key in renderLayersDict:
    emplacement=get_emplacement(key)
    print(emplacement)
    create_shot(key,0.1,-4.3-(2.97*emplacement))
    shotNum+=1