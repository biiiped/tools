import nuke
import json



def create_animated_locators_from_json(json_path):

    # Load the JSON file
    with open(json_path, 'r') as file:
        animation_data = json.load(file)

    # Dictionary to hold Axis nodes for each point number, ensuring only one node per point
    point_nodes = {}

    # Process each frame in the animation data
    for frame_info in animation_data:
        frame_number = int(frame_info['frame'])  # Ensure frame number is an integer
        points = frame_info['points']

        # Process each point in the current frame
        for point_data in points:
            point_number = point_data['point_number']
            position = point_data['position']

            # Ensure position values are floats
            pos_x = float(position['x'])
            pos_y = float(position['y'])
            pos_z = float(position['z'])
            

            # If an Axis node for this point doesn't exist, create it
            if point_number not in point_nodes:
                axis_node = nuke.createNode('Axis2')
                point_nodes[point_number] = axis_node
                axis_node.setInput(0, None)  # Ensure no input connections

            # Get the Axis node from the dictionary
            axis_node = point_nodes[point_number]

            # Set keyframes for the position at the current frame
            for index, value in enumerate([pos_x, pos_y, pos_z]):
                axis_node['translate'].setValueAt(value, frame_number, index)
                print('value set at '+str(frame_number))


# Path to the JSON file (update this path as necessary)
json_file_path = "D:/guilhem/transforms_animated.json"

# Call the function to create and animate locators
create_animated_locators_from_json(json_file_path)