import nuke
import os

# Path to your script
script_path = os.path.expanduser("//MINERVA/3d4_23_24/MECHA/02_ressource/@LOUIS/ressources/MCH_scriptPublish/nukeImportShot.py")

# Function to run the script
def run_my_script():
    exec(open(script_path).read())

# Add a button to the Nuke interface
nuke.menu('Nuke').addCommand('Custom/importShot', 'run_my_script()')