import hou
import os




def renderAutoFill(input_string):
    seq,sh,rdLayer=input_string.split("_")
    hou.node(".").parm("shot").set(sh)
    hou.node(".").parm("sequence").set(seq)
    hou.node(".").parm("renderLayer").set(rdLayer)

