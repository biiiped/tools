import cv2
import os
import sys
from PySide6.QtWidgets import *

def high_lighted_text(input_image,text,x,y,font_scale):
    # Set the font scale and thickness for the border
    font_scale = 1
    font_thickness = 2
    border_thickness = 5
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (255, 255, 255)
    hilight_color = (0, 0, 0)

    # Get the size of the text
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)

    # Calculate the position for the border
    x1 = x - border_thickness
    y1 = y - border_thickness-text_size[1]
    x2 = x + text_size[0] + border_thickness
    y2 = y + text_size[1] + border_thickness-text_size[1]

    # Draw the black border
    cv2.rectangle(input_image, (x1, y1), (x2, y2), hilight_color, -1)  # -1 fills the rectangle
    cv2.putText(input_image, text, (x, y), font, font_scale, text_color, font_thickness)


def check_if_path_exist(path):
    if os.path.exists(path):
        print(f"The path '{path}' exists.")
    else:
        print(f"The path '{path}' does not exist.")


def add_name_and_frame_count_to_video(file_input, output_directory):
    print("starting with"+file_input)
    check_if_path_exist(file_input)

    directory_path=os.path.dirname(file_input)
    basename=os.path.basename(file_input)
    filename=os.path.splitext(basename)[0]
    extension=os.path.splitext(basename)[1]

    # Specify the output directory
    output_directory = os.path.abspath(output_directory)
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    file_output = os.path.join(output_directory, filename + "_com" + extension)
    print("creation of " + file_output)

    # Ouvrir la vidéo d'entrée
    input_video = cv2.VideoCapture(file_input)
    print(input_video)

    # Récupérer les propriétés de la vidéo (taille, framerate, etc.)
    frame_width = int(input_video.get(3))
    frame_height = int(input_video.get(4))
    fps = int(input_video.get(5))


    # Créer un objet VideoWriter pour écrire la vidéo de sortie
    output_video = cv2.VideoWriter(file_output, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Boucle à travers chaque frame de la vidéo
    frame_count = 1
    while True:
        ret, frame = input_video.read()
        if not ret:
            break
        high_lighted_text(frame,filename,50,50,1)
        frame_counter="f "+str(frame_count)
        high_lighted_text(frame,frame_counter,50,100,1)
        output_video.write(frame)
        print(frame_counter)
        frame_count+=1

    # Fermer les objets de vidéo
    input_video.release()
    output_video.release()

    # Fermer toutes les fenêtres OpenCV
    cv2.destroyAllWindows()
    print("finished !")

app = QApplication(sys.argv)
options = QFileDialog.Options()
options |= QFileDialog.ReadOnly  # Allow selecting read-only files
files, _ = QFileDialog.getOpenFileNames(None,"Select Files","","All Files (*);;Text Files (*.txt);;Python Files (*.py)",options=options,)

if files:
    print("Selected Files:")
    for file in files:
        print(file)
        output_directory = r"\\MINERVA\3d4_23_24\MECHA\08_editing\input\02_animatique3D\shots_avec_fCount"
        add_name_and_frame_count_to_video(file,output_directory)


QApplication.exit()



