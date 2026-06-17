import hou

def find_and_replace_in_files(find,replace):
    # Get all nodes in the Houdini scene
    all_nodes = hou.node("/").allSubChildren()
    
    for node in all_nodes:
        # Iterate through all parameters in the node
        for parm in node.parms():
            if parm.name() == "file":  # Check if the parameter is named 'filename'
                current_value = parm.evalAsString()
                if "png" in current_value:  # Check if "png" is in the parameter's value
                    new_value = current_value.replace(find, replace)  # Replace "png" with "exr"
                    parm.set(new_value)  # Update the parameter value
                    print(f"Updated {node.path()} parameter 'filename' to: {new_value}")

# Run the function
find="custom"
replace="custom/outputSRGB"
find_and_replace_in_files(find,replace)
