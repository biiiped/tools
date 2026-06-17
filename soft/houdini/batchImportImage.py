import hou

import os

editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
imageDir = r"M:\MECHA\02_ressource\@LOUIS\ressources\thumbnail\seq040"
images = os.listdir(imageDir)

png_files = [file_path for file_path in images if file_path.lower().endswith(".png")]
houdiniImageList=[]


pan=1
size=3
orientation='y'



if orientation == 'y':
    offset=0.45
else:
    offset=1.05

pan=pan*offset
pan=pan*size

left=0
bot=size
right=size
top=0

for imageName in png_files:
    if orientation == 'y':
        bot+=pan
        top+=pan
    else:
        left+=pan
        right+=pan
    image = hou.NetworkImage()
    imagePath = os.path.join(imageDir, imageName)
    image.setPath(imagePath)
    
    image.setRect(hou.BoundingRect(left, bot, right, top))
    houdiniImageList.append(image)
    
editor.setBackgroundImages(houdiniImageList)

    




