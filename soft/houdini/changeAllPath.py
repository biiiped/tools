import hou

# Define the old and new path prefixes
old_prefix = "//MINERVA/3d4_23_24/MECHA/"
new_prefix = "$JOB/"

# Get all nodes in the scene
all_nodes = hou.node("/").allSubChildren()

# Loop through each node
for node in all_nodes:
    # Loop through each parameter
    for parm in node.parms():
        # Get the current parameter value
        value = parm.evalAsString()

        # Check if the value contains the old path prefix
        if old_prefix in value:
            # Replace it with the new prefix
            new_value = value.replace(old_prefix, new_prefix)
            parm.set(new_value)
            print(f"Updated: {node.path()} | {parm.name()} → {new_value}")

print("Path replacement completed.")
