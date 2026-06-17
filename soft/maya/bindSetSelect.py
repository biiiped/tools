import maya.cmds as cmds

def create_selection_set(nodes, set_name):
    # Check if the selection set already exists, if yes, delete it
    if cmds.objExists(set_name):
        cmds.delete(set_name)

    # Create a new selection set
    selection_set = cmds.sets(name=set_name, empty=True)

    # Add nodes to the selection set
    cmds.sets(nodes, edit=True, addElement=selection_set)
    
    return selection_set

def main():
    # Find all nodes with "bind_" in their names
    bind_nodes = cmds.ls("*bind_*", type="joint")
    ribbons_bind_nodes = cmds.ls("*bind_ribbonJnt*", type="joint")

    if not bind_nodes:
        print("No nodes with 'bind_' found.")
        return

    # Specify the name for the selection set
    selection_set_name = "bind_nodes_set"
    selection_set_name2 = "bind_ribbon_nodes_set"

    # Create a selection set with the found nodes
    create_selection_set(bind_nodes, selection_set_name)
    create_selection_set(ribbons_bind_nodes, selection_set_name2)

    print(f"Selection set '{selection_set_name}' created with {len(bind_nodes)} nodes.")

if __name__ == "__main__":
    main()
