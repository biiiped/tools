import cv2
import os

def main(folder_path, output_file):
    # Get list of image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    image_files.sort()  # Sort files to maintain order

    if not image_files:
        print("No image files found in the specified folder.")
        return

    # Read the first image to get dimensions
    first_image_path = os.path.join(folder_path, image_files[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape

    # Define the codec and createS VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' for .mp4 files
    video_writer = cv2.VideoWriter(output_file, fourcc, 30.0, (width, height))

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        frame = cv2.imread(image_path)
        video_writer.write(frame)

    video_writer.release()


def create_mp4_beside_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    output_file = os.path.join(folder_path, folder_name + ".mp4"s)
    main(folder_path, output_file)
