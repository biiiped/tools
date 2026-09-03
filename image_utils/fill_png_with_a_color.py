from PIL import Image
import sys
import os

def whiten_keep_alpha(input_path, output_path, color):
    img = Image.open(input_path).convert("RGBA")
    r, g, b, a = img.split()

    # Create a solid color image for RGB, keep original alpha
    colored = Image.new("RGBA", img.size, (*color, 255))
    colored.putalpha(a)

    colored.save(output_path)

folder = r"S:\ressource\Image\texture\logos\softwareLogo\uniformSoftLogo\black"
for image in os.listdir(folder):
    if image.endswith(".png"):
        input_path = os.path.join(folder, image)
        output_path = os.path.join(folder, f"{image}_white.png")
        whiten_keep_alpha(input_path, output_path, (255, 255, 255))  # Example color: white