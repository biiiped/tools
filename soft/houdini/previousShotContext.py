import hou
import os

currentShot=hou.contextOption("shot")
print(type(currentShot))

nextShot=int(currentShot)-1
hou.setContextOption("shot", nextShot)