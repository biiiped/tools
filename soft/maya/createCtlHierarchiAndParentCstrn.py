import maya.cmds as cmds

def create_controls_for_bones():
    # Get the selected root bone
    selected_bones = cmds.ls(selection=True, type="joint")
    if not selected_bones:
        cmds.error("Please select the root joint of the bone hierarchy.")
        return

    def create_ctl_for_bone(bone):
        # Create the control
        ctl_name = bone.replace("JNT", "CTL")  # Replace 'jnt' with 'CTL' in the name
        ctl = cmds.circle(name=ctl_name, normal=(1, 0, 0), radius=1.5)[0]
        
        # Create a group for the control to maintain offsets
        grp_name = ctl.replace("CTL", "GRP")
        ctl_grp = cmds.group(ctl, name=grp_name)

        # Match the group position to the bone's position
        cmds.delete(cmds.pointConstraint(bone, ctl_grp))
        cmds.delete(cmds.orientConstraint(bone, ctl_grp))

        # Parent constrain the bone to the control
        cmds.parentConstraint(ctl, bone, maintainOffset=True)

        return ctl, ctl_grp

    def process_hierarchy(bone, parent_ctl=None):
        ctl, ctl_grp = create_ctl_for_bone(bone)
        
        # Parent the control's group to the parent control (if exists)
        if parent_ctl:
            cmds.parent(ctl_grp, parent_ctl)
        
        # Process child bones
        children = cmds.listRelatives(bone, children=True, type="joint")
        if children:
            for child in children:
                process_hierarchy(child, ctl)

    # Start processing from the root bone
    process_hierarchy(selected_bones[0])

# Run the function
create_controls_for_bones()
