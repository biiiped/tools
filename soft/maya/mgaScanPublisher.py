import os
import shutil

mgaPath=r"D:\megascan\Downloaded\3d\nature_rock_ukopeijs"
assetPath=r"\\MINERVA\3d4_23_24\MECHA\04_asset\03_item"
ldvTemplatePath=r"\\MINERVA\3d4_23_24\MECHA\02_ressource\@LOUIS\MCH_Template\MCH_template_ldv_014.hipnc"
previewPath=r"\\MINERVA\3d4_23_24\MECHA\.pinpin_data\icons"
geopath=r"\\MINERVA\3d4_23_24\MECHA\09_publish\asset\03_item\geo"
texturePath=r"\\MINERVA\3d4_23_24\MECHA\10_texture\03_item"


def find_files(folder_path,end):
    preview_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(end):
                preview_files.append(os.path.join(root, file))
    return preview_files

def create_folder(folder_name):
    try:
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")

txtpath=find_files(mgaPath,".txt")[0]
file_name = os.path.basename(txtpath)
name = os.path.splitext(file_name)[0]
print(name)

create_folder(os.path.join(assetPath,name))
create_folder(os.path.join(assetPath,name,"houdini"))
create_folder(os.path.join(assetPath,name,"houdini","ldv"))
ldvDir=os.path.join(assetPath,name,"houdini","ldv")
ldvName=f"MCH_itm_{name}_ldv_E_001.hipnc"

shutil.copyfile(ldvTemplatePath, os.path.join(ldvDir,ldvName))


geo=find_files(mgaPath,"_LOD0.fbx")[0]
geoName=f"MCH_itm_{name}_geo_P.fbx"
shutil.copyfile(geo, os.path.join(geopath,geoName))


preview=find_files(mgaPath,"Preview.png")[0]
previewName=name.capitalize()+".png"
shutil.copyfile(preview, os.path.join(previewPath,previewName))




assetTexturePath=os.path.join(texturePath,name)
create_folder(assetTexturePath)

normal=find_files(mgaPath,"_Normal_LOD0.jpg")[0]
normalName=f"MCH_{name}_normal.jpg"
shutil.copyfile(normal, os.path.join(assetTexturePath,normalName))

diplacement=find_files(mgaPath,"_Displacement.exr")[0]
diplacementName=f"MCH_{name}_diplacement.exr"
shutil.copyfile(diplacement, os.path.join(assetTexturePath,diplacementName))

albedo=find_files(mgaPath,"_Albedo.jpg")[0]
albedoName=f"MCH_{name}_albedo.exr"
shutil.copyfile(albedo, os.path.join(assetTexturePath,albedoName))

roughness=find_files(mgaPath,"_Roughness.jpg")[0]
roughnessName=f"MCH_{name}_roughness.jpg"
shutil.copyfile(roughness, os.path.join(assetTexturePath,roughnessName))

