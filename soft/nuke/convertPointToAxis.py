for info in nukescripts.snap3d.selectedVertexInfos():
    position = info.position
    axisNode = nuke.nodes.Axis()
    axisNode['translate'].setValue(position)