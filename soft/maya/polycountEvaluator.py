import maya.cmds as cmds
import maya.mel as mel


def get_poly_count(node):
    # Get the polygon count for the specified node
    poly_count = cmds.polyEvaluate(node, vertex=True)
    
    return poly_count

def get_volume(node):
    bbox_dimensions = cmds.getAttr(node + '.boundingBoxSize')[0]
    volume = bbox_dimensions[0] * bbox_dimensions[1] * bbox_dimensions[2]
    
    return volume

def format_number(num):
    # Convert the number to a float with one decimal place
    num_float = float(num)

    # Check if the number is greater than or equal to 1000
    if num_float >= 1000:
        # Format the number to one decimal place and divide by 1000
        formatted_num = "{:.1f}k".format(num_float / 1000)
    else:
        # Format the number to one decimal place
        formatted_num = "{:.1f}".format(num_float)

    return formatted_num

sl= cmds.ls(sl=True)
print("starting")

density_dict = {}

for node in sl:
    childrens=cmds.listRelatives(node,allDescendents=True)
    print(f"children {childrens}")
    for children in childrens:
        print(f"children {children}")
        isShape=cmds.objectType(children, isAType='shape')
        print(f"isShape {isShape}")
        if not isShape:
            #print(f"{children} is not a shape")
            pass
        else:
            polycount=get_poly_count(children)
            polycountReformated=format_number(polycount)
            print(f"node: {children}")
            print(f"have {polycountReformated} poly")

            volume=get_volume(children)
            volumeReformated=format_number(volume)
            print(f"have a volume of {volumeReformated} cm3")
            print("")

            density =polycount/(volume/1000000)
            print(f"have a density of {density} poly par m3")

            density_dict[children] = {
                'polycount': polycount,
                'volume': volume,
                'density': density
            }

# Sort the dictionary items based on the 'density' value in descending order
sorted_data = sorted(density_dict.items(), key=lambda x: x[1]['density'], reverse=True)

sorted_data2 = sorted(density_dict.items(), key=lambda x: x[1]['polycount'], reverse=True)

# Print the top 10 elements with the biggest density
for i in range(min(10, len(sorted_data))):
    key, value = sorted_data[i]
    densitiReformated=format_number(value['density'])

    print(f"node {i} {key} have a density of {densitiReformated} per m3")
print("")

for i in range(min(10, len(sorted_data2))):
    key, value = sorted_data2[i]
    polycountReformated=format_number(value['polycount'])

    print(f"node {i} {key} have a density of {polycountReformated} per m3")

print("end")

