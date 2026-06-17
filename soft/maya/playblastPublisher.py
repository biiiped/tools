import maya.cmds as cmds

# Get the current Maya scene file name
maya_file_name = cmds.file(q=True, sn=True)
print(f"maya_file_name={maya_file_name}")

# Check if the scene has been saved
if maya_file_name:

    # Construct the playblast output file name based on the Maya file name
    playblast_file_name = os.path.splitext(os.path.basename(maya_file_name))[0] + ".mov"
    playblast_directory = r"\\MINERVA\3d4_23_24\MECHA\08_editing\input\02_animatique3D"  # Specify your desired directory here
    playblast_file_path = os.path.join(playblast_directory, playblast_file_name)
    print(f"playblast_file_path={playblast_file_path}")

    # Perform the playblast
    cmds.playblast(
        format="qt",
        filename=playblast_file_path,
        forceOverwrite=True,
        sequenceTime=0,
        clearCache=True,
        viewer=True,
        showOrnaments=True,
        fp=4,
        percent=100,
        compression="H.264",
        quality=100,
        widthHeight=[2048, 858]
    )
else:
    print("Please save the Maya scene before running the playblast.")