import maya.cmds as cmds
import json



def saveConstraint(old_root,json_file):
    """Transfer constraints from old_root to new_root."""
    constraints = cmds.listRelatives(old_root, allDescendents=True, type='constraint') or []
    constraints_data = {}

    for con in constraints:
        constrained_objs = cmds.listConnections(con + ".constraintParentInverseMatrix", s=True, d=False) or []
        if not constrained_objs:
            print(f"No constrained object found for {con}")
            continue

        target_name = '_'.join(con.split('_')[:-1])
        con_input=cmds.listConnections(f'{con}.target[0].targetParentMatrix', source=True, destination=False)
        constraint_type = cmds.nodeType(con)

        constraints_data[con] = {
            "type": constraint_type,
            "input": con_input,
            "output": constrained_objs
        }
    with open(json_file, 'w') as f:
        json.dump(constraints_data, f, indent=4)


def create_constraints_from_json(json_data):
    for constraint_name, constraint_info in json_data.items():
        constraint_type = constraint_info['type']
        inputs = constraint_info['input']
        outputs = constraint_info['output']

        for output in outputs:
            if constraint_type == "parentConstraint":
                cmds.parentConstraint(inputs, output, mo=True, name=constraint_name)
            elif constraint_type == "scaleConstraint":
                cmds.scaleConstraint(inputs, output, mo=True, name=constraint_name)
            else:
                print(f"Unsupported constraint type: {constraint_type}")


# Example usage
old_geo = "geo"
#saveConstraint(old_geo,r"C:\Users\l.bonnaud\Desktop\caca.json")


with open(r"C:\Users\l.bonnaud\Desktop\caca.json", 'r') as f:
    json_data = json.load(f)
create_constraints_from_json(json_data)