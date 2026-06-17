import hou

list = [
    "diamondBaguette", "diamondBaguetteStraight", "diamondBriolette", "diamondCalf", "diamondCushion", 
    "diamondCushionSquare", "diamondDrop", "diamondElypse", "diamondEmerald", "diamondEmeraldSquare", 
    "diamondFrench", "diamondHalfMoon", "diamondHeartA", "diamondHeartB", "diamondHeartC", 
    "diamondLozenge", "diamondMarquise", "diamondOctagonA", "diamondOctagonB", "diamondOldEuropian", 
    "diamondOval", "diamondPear", "diamondPeruzzi", "diamondPrincess", "diamondRadiant", 
    "diamondRadiantSquare", "diamondRectangle", "diamondRound", "diamondRuby", "diamondSphereA", 
    "diamondSphereB", "diamondSquare", "diamondTable", "diamondTaperedBaguette", "diamondTriangle", 
    "diamondTrillionCurved", "diamondTrillionStraight"
]



x=0
selected_node = hou.selectedNodes()[0]
for item in list:
    duplicate_node = hou.copyNodesTo([selected_node], selected_node.parent())[0]
    duplicate_node.parm('diamond').set(x)
    duplicate_node.setName(item, unique_name=True)
    x+=1
