def main():
    import argparse
    import os
    import cv2

    parser = argparse.ArgumentParser(description="Create an MP4 video from an image sequence.")
    parser.add_argument("image_folder", type=str, help="Path to the folder containing the image sequence.")
    parser.add_argument("output_video", type=str, help="Path to the output MP4 video file.")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for the output video.")
    args = parser.parse_args()

    # Get list of images in the folder
    images = [img for img in os.listdir(args.image_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
    images.sort()  # Sort images by name

    if not images:
        print("No images found in the specified folder.")
        return

    # Read the first image to get dimensions
    first_image_path = os.path.join(args.image_folder, images[0])
    frame = cv2.imread(first_image_path)
    height, width, layers = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    video_writer = cv2.VideoWriter(args.output_video, fourcc, args.fps, (width, height))

    for image in images:
        image_path = os.path.join(args.image_folder, image)
        frame = cv2.imread(image_path)
        video_writer.write(frame)

    video_writer.release()