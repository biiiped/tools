import nuke
import os

# Path to your script

script_path = os.path.expanduser("R:/script/script nuke/nukeConvertPointToAxis.py")

# Function to run the script
def run_my_script():
    exec(open(script_path).read())

# Add a button to the Nuke interface
nuke.menu('Nuke').addCommand('Custom/nukeConvertPointToAxis', 'run_my_script()')