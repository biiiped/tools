import os
import hou
import re



texture_path = '//MINERVA/3d4_23_24/WILSON/10_texture'

#Initialize 
publish_file = hou.node("/stage/ldv_template").parm("publish_path").eval()
file_name = os.path.splitext(os.path.basename(publish_file))[0]
file_name_parts = file_name.split('_')
shortType = file_name_parts[1]
print(f"shortType:{shortType}")
name = file_name_parts[2]
print(f"name:{name}")
if shortType == "chr":
    tex_path = texture_path+ "/01_char/"
if shortType == "prp":
    tex_path = texture_path + "/02_prop/"
if shortType == "itm":
    tex_path = texture_path + "/03_item/"
if shortType == "env":
    tex_path = texture_path + "/04_enviro/"
    
tex_directory = tex_path + name + '/'
print(tex_directory)

# texture channels name
texture_channels = ['albedo', 'diffuseColor','rough','roughness','normal','disp', 'displacement','specular','spec', 'sssColor', 'sss_gain','Height','bump']
 
# Define the input indices for each texture channel
shader_input_index = {
    'albedo': 1,
    'diffuseColor':1,
    'rough': 6,
    'roughness':6,
    'spec': 4,
    'specular':4,
    'sssColor': 18,
    'sssGain': 17,
    'normal': 39   
}

#UDIM
udim_pattern = r'\d{4}(?=\.\w+$)'
udim_token = '<UDIM>'
 
# Set texture directory

# Context
materialLibPath = hou.parm("matLib").evalAsString()
materialLib = hou.node(materialLibPath)

if materialLib:
    # Create a PxrMaterialBuilder node and PxrSurface node
    arnBuilder = materialLib.createNode("arnold_materialbuilder", f"{name}_ARN_build")
    arnold_mat = arnBuilder.children()[0]
    print(arnold_mat)
    standard_surface = arnBuilder.createNode("arnold::standard_surface", f"{name}_surface")
    arnold_mat.setInput(0, standard_surface)
    # Create a dictionary to store channel-specific texture lists
    channel_texture_dict = {channel: [] for channel in texture_channels}
    


    for texture in os.listdir(tex_directory):
        filename, ext = os.path.splitext(texture)
        for channel in texture_channels:
            if name[1] in texture and channel in texture:
                channel_texture_dict[channel].append(texture)

    # Create a single 'pxrTexture' node for each channel
    for channel in texture_channels:
        channel_textures = channel_texture_dict[channel]
        if channel_textures:
            node_name = f"{name}_{channel}"
            file_paths = [os.path.join(tex_directory, t) for t in channel_textures]
            # Replace UDIM sequences with <UDIM> in filenames
            file_paths_with_udim = [re.sub(udim_pattern, udim_token, filename) for filename in file_paths]
            # Create one 'pxrTexture' node for this channel
            image_node = arnBuilder.createNode('arnold::image', 'img_' + node_name)
           
            image_node.parm('filename').set(file_paths_with_udim[0])
            if channel == 'albedo' or channel =='diffuseColor':
                image_node.parm('color_family').set('ACES')
            else : 
                image_node.parm('color_family').set('Utility')
            # Connect the 'pxrTexture' node to the corresponding input on 'pxrsurface'
            input_index = shader_input_index.get(channel)
            if input_index is not None:
                if '_gain' in channel :
                    standard_surface.setInput(input_index, image_node, 1)
                else :
                    standard_surface.setInput(input_index, image_node)

            # Check if this is the 'nmm' channel and add 'pxrNormalMap' node
            if channel == 'normal':
                arn_normal_map = arnBuilder.createNode('arnold::normalmap', node_name + '_Normal')
                arn_normal_map.setInput(1, image_node)
                standard_surface.setInput(39, arn_normal_map)  # Connect to the Normal input of pxrSurface
            if channel == 'rough' or channel == 'roughness':
                arn_range = arnBuilder.createNode('arnold::range', node_name + '_Range')
                arn_range.setInput(0, image_node)
                standard_surface.setInput(6, arn_range, 1)  # Connect to the Displacement input of pxrSurface
            # Check if this is the 'disp' channel and add 'pxrRemap' node
            if channel == 'disp' or channel == 'displacement':
                arnold_mat.setInput(1, image_node,1)
                

else :
    print('no material library node found : use absolute path ')

arnBuilder.layoutChildren()
