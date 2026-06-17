import os
import hou
import json
import re



"""
def main():

    version=1

    hou_session = hou.hipFile
    file_path = hou_session.name()
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    file_name_parts = file_name.split('_')
    stage = hou.node('/stage')

    # Extract the seq and the shot
    seqID = file_name_parts[1]
    #print(f"seq:{seqID}")
    shID = file_name_parts[2]
    #print(f"sh:{shID}")

    #create version label
    updateNode=hou.node(f"/stage/updateScene")

    #get file version:

    try :
        parm_group = updateNode.parmTemplateGroup()
    except Exception as e:
        print(e)
        print(f"i do not find /stage/"+updateNode)
        
    existing_parm = parm_group.find('version_label')
    if existing_parm is None:
        fileversion=0
        version_label_parm_template = hou.LabelParmTemplate(name="version_label", label="V ."+str(version))
        parm_group.append(version_label_parm_template)
        updateNode.setParmTemplateGroup(parm_group)
    else:
        fileversion=existing_parm.label()

    print(f"file version =  {fileversion}" )
    print(f"script version =V .{version}" )

    if fileversion==0:
        camera=hou.node(f"/stage/motion_blur")
        camera.parm('xn__shutteropen_0ta').set(-0.1)
        camera.parm('xn__shutterclose_nva').set(0.1)
        print("setting motion blur to 0.1")


        



    





    #create CamVis_crypto
    CamVis_crypto_fx=hou.node(f"/stage/CamVis_crypto_fx")
    if CamVis_crypto_fx is None:
        print ("CamVis_crypto_fx is not here")
        pruneLight=hou.node(f"/stage/prune_light1")
        matLib=hou.node(f"/stage/materiallibrary1")

        CamVis_crypto_fx=create_node("CamVis_crypto_fx","rendergeometrysettings","/stage/",pruneLight,matLib)

        CamVis_crypto_fx.parm("primpattern").set(f"/MCH_{seqID}_{shID}_lighting_P/fx/**")
        CamVis_crypto_fx.parm("xn__primvarsarnoldvisibilitycamera_control_02bgk").set("set")
        CamVis_crypto_fx.parm("xn__primvarsarnoldvisibilitycamera_zpbgk").set(0)
        print ("CamVis_crypto_fx created !")
    else:
        pass

    
    #create volume_light_on
    volume_light_on=hou.node(f"/stage/volume_light_on")
    if volume_light_on is None:
        print ("volume_light_on is not here")
        motionBlur=hou.node(f"/stage/motion_blur")
        matall=hou.node(f"/stage/matte_all")

        volume_light_on=create_node("volume_light_on","light::2.0","/stage/",motionBlur,matall)

        parameters = volume_light_on.parms()
        
        volume_light_on.parm("primpattern").set(f"%type:Light")
        volume_light_on.parm("createprims").set("off")
        volume_light_on.parm("initforedit").set("setdonothing")

        volume_light_on.parm("xn__xformOptransform_control_6fb").set("none")

        volume_light_on.parm("xn__inputsintensity_control_jeb").set("none")
        volume_light_on.parm("xn__inputsexposure_control_wcb").set("none")
        volume_light_on.parm("xn__inputscolor_control_06a").set("none")
        volume_light_on.parm("xn__inputsenableColorTemperature_control_pzb").set("none")
        volume_light_on.parm("xn__inputscolorTemperature_control_xpb").set("none")
        volume_light_on.parm("xn__inputstexturefile_control_shbh").set("none")
        volume_light_on.parm("xn__inputsradius_control_n8a").set("none")
        volume_light_on.parm("xn__inputswidth_control_06a").set("none")
        volume_light_on.parm("xn__inputsheight_control_n8a").set("none")

        volume_light_on.parm("xn__inputslength_control_n8a").set("none")
        volume_light_on.parm("xn__inputsangle_control_06a").set("none")
        volume_light_on.parm("xn__houdiniclippingRange_control_pmb").set("none")
        volume_light_on.parm("xn__inputsnormalize_control_jeb").set("none")
        volume_light_on.parm("xn__inputsdiffuse_control_99a").set("none")
        volume_light_on.parm("xn__inputsspecular_control_wcb").set("none")
        volume_light_on.parm("xn__houdiniguidescale_control_thb").set("none")
        volume_light_on.parm("xn__houdiniinviewermenu_control_2kb").set("none")
        volume_light_on.parm("xn__lightfilters_control_m8a").set("none")

        volume_light_on.parm("xn__inputsshapingconeangle_control_xpbhe").set("none")
        volume_light_on.parm("xn__inputsshapingconesoftness_control_tubhe").set("none")
        volume_light_on.parm("barndoorleft_control").set("none")
        volume_light_on.parm("barndoorleftedge_control").set("none")
        volume_light_on.parm("barndoorright_control").set("none")
        volume_light_on.parm("barndoorrightedge_control").set("none")
        volume_light_on.parm("barndoortop_control").set("none")
        volume_light_on.parm("barndoortopedge_control").set("none")
        volume_light_on.parm("barndoorbottom_control").set("none")
        volume_light_on.parm("barndoorbottomedge_control").set("none")
        volume_light_on.parm("xn__inputsshapingfocus_control_fjbh").set("none")
        volume_light_on.parm("xn__inputsshapingfocusTint_control_xpbh").set("none")
        volume_light_on.parm("xn__inputsshapingiesfile_control_ombhd").set("none")
        volume_light_on.parm("xn__inputsshapingiesnormalize_control_tubhd").set("none")
        volume_light_on.parm("xn__inputsshapingiesangleScale_control_gwbhd").set("none")
        

        volume_light_on.parm("arnoldaov_control").set("none")


        volume_light_on.parm("arnoldvolume_control").set("set")
        volume_light_on.parm("xn__primvarsarnoldvolume_p8ag").set(1)


        print ("volume_light_on created !")
    else:
        pass

    #change des settings de la scenes
    render_settings_nodes = []
    for node in stage.allSubChildren():
        #check rendersetting cam path
        if 'rendersettings' in node.type().name():
            camPath=f"/MCH_{seqID}_{shID}_lighting_P/camera/{shID}/shotCam/shotCamShape"
            render_settings_nodes.append(node.path())
            node.parm('camera_control').set("set")
            node.parm('camera').set(camPath)

        #check goliath rick zeke and shark path
        charalist=["rick","zeke","shark","goliath"]
        for chara in charalist:
            if f'unmatte_{chara}' in node.name():
                node.parm('primpattern').set(f"*/chara/{chara}/**")

        #check for props
        proplist=["citerne","sword"]
        for prop in proplist:
            if f'unmatte_{prop}' in node.name():
                node.parm('primpattern').set(f"*/prop/{prop}/**")


    #connecte les render settings
    ctrlNode=hou.node(f"/stage/{shID}")

    try :
        parm_group = ctrlNode.parmTemplateGroup()
    except Exception as e:
        print(e)
        print(f"i do not find /stage/{shID}")

    existing_parm = parm_group.find('threshold')
    if existing_parm is None:
        #add maxsample to ctl
        maxsample_parm_name = 'maxSample'
        maxsample_parm_label = 'maxSample'
        maxsample_parm_default = [3]
        maxsample_parm_template = hou.IntParmTemplate(maxsample_parm_name, maxsample_parm_label,1, default_value=(maxsample_parm_default),min=1,max=30)
        parm_group.append(maxsample_parm_template)
        #add treshold to ctl
        threshold_parm_name = 'threshold'
        threshold_parm_label = 'threshold'
        threshold_parm_default = [0.1]
        threshold_parm_template = hou.FloatParmTemplate(threshold_parm_name, threshold_parm_label,1, default_value=(threshold_parm_default),min=0,max=1.0)
        parm_group.append(threshold_parm_template)

        ctrlNode.setParmTemplateGroup(parm_group)

        stage = hou.node('/stage')
        render_settings_nodes = []
        for node in stage.allSubChildren():
            if 'rendersettings' in node.type().name():
                render_settings_nodes.append(node.path())
        
        for RDS in render_settings_nodes:
            rendersettingsNode=hou.node(RDS)
            output_connections = rendersettingsNode.outputConnections()
            for connection in output_connections:
                connected_node = connection.outputNode()
                outputname=connected_node.name()

            rendersettingsNode.setName("renderSettings_"+outputname, unique_name=True)
            #set progressive render to off
            rendersettingsNode.parm('xn__arnoldglobalenable_progressive_render_control_dfcg').set("set")
            rendersettingsNode.parm('xn__arnoldglobalenable_progressive_render_c1bg').set(0)
            #set adaptive render to on
            rendersettingsNode.parm('xn__arnoldglobalenable_adaptive_sampling_control_qdcg').set("set")
            rendersettingsNode.parm('xn__arnoldglobalenable_adaptive_sampling_pzbg').set(1)
            #connect max sample to ctl
            rendersettingsNode.parm('xn__arnoldglobalAA_samples_max_control_gwbg').set("set")
            expression1=f'ch("../{shID}/maxSample")'.format(shID)
            rendersettingsNode.parm('xn__arnoldglobalAA_samples_max_fjbg').setExpression(expression1)
            #connect threshold to ctl
            rendersettingsNode.parm('xn__arnoldglobalAA_adaptive_threshold_control_u7bg').set("set")
            expression2=f'ch("../{shID}/threshold")'.format(shID)
            rendersettingsNode.parm('xn__arnoldglobalAA_adaptive_threshold_tubg').setExpression(expression2)

        print(f"this file has been updated ! {version}")

    

    else :
        pass
"""
def create_node(name,type,path,output):
    print ("creating node ") 
    node=hou.node(path).createNode(type, name)
    outputPos=output.position()
    node.move((outputPos[0],outputPos[1]-0.5))
    output.setInput(0, node)
    return node

obj = hou.node('/obj')
for node in obj.allSubChildren():
    print(node.name)
    #create null
    create_node("null","null",obj,node)