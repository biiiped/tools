'''
this script duplicate was used for cam map in the swaDisney advertisement, it duplicate a node fo each png in a folder
'''

import os
import hou

def create_nodes_from_pngs(folder_path, parent_node):
    """
    Duplicate an existing "edit_texture" node for each PNG file in the specified folder,
    then create a null node and connect the duplicated node to it.

    :param folder_path: Path to the folder containing PNG files.
    :param parent_node: The Houdini node where the new nodes will be created.
    """
    if not os.path.exists(folder_path):
        hou.ui.displayMessage(f"Folder not found: {folder_path}")
        return

    # List all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]

    if not png_files:
        hou.ui.displayMessage("No PNG files found in the specified folder.")
        return

    # Find the "edit_texture" node to duplicate
    edit_texture_node = parent_node.node("edit_texture")
    if not edit_texture_node:
        hou.ui.displayMessage("No node named 'edit_texture' found in the parent node.")
        return
    n=0
    # Create nodes for each PNG file
    for png_file in png_files:
        png_path = os.path.join(folder_path, png_file).replace('\\', '/')
        
        try:
            # Duplicate the "edit_texture" node
            node_name = os.path.splitext(png_file)[0]
            new_edit_node = edit_texture_node.copyTo(parent_node)
            new_edit_node.setName(f"edit_texture_{node_name}", unique_name=True)
            new_edit_node.setPosition((n, 0))
            attribute_name = "xn__inputsfile_dsa"
            new_edit_node.parm(attribute_name).set(png_path)

            # Create a null node
            null_node = parent_node.createNode("null", node_name)
            null_node.setName(node_name, unique_name=True)
            null_node.setPosition((n, -2))

            # Connect the new edit node to the null node
            null_node.setInput(0, new_edit_node)


            # Layout the nodes nicely

            n+=2
        except Exception as e:
            print(f"Error creating nodes for {png_file}: {e}")


# Example usage:
# Update the folder path to your PNG directory
folder_path = hou.ui.selectFile(title="Select PNG Folder", file_type=hou.fileType.Directory)
parent_node = hou.node("/stage")  # Change to your desired network path (LOPs context)

if folder_path and parent_node:
    create_nodes_from_pngs(folder_path, parent_node)
