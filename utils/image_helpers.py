import os
from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk

def insert_circular_image(canvas, image_path, size=(300, 300)):
    """
    Insert a circular cropped image into a Tkinter canvas.

    Args:
        canvas (tk.Canvas or ctk.CTkCanvas): Canvas to insert the image into.
        image_path (str): Path to the image file.
        size (tuple): Size of the image (width, height).
    """
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    try:
        image = Image.open(image_path).resize(size, Image.LANCZOS)

        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)

        circular_image = Image.new("RGBA", size, (0, 0, 0, 0))
        circular_image.paste(image, (0, 0), mask)

        canvas.image = ImageTk.PhotoImage(circular_image)
        canvas.create_image(size[0] // 2, size[1] // 2, image=canvas.image)

    except Exception as e:
        print(f"Error inserting circular image: {str(e)}")

def load_image(path, resize_to=None):
    """
    Load an image and optionally resize it.

    Args:
        path (str): Path to the image.
        resize_to (tuple): (width, height) to resize, optional.

    Returns:
        PIL ImageTk.PhotoImage object or None if error.
    """
    if not os.path.exists(path):
        print(f"Image not found: {path}")
        return None

    try:
        image = Image.open(path)
        if resize_to:
            image = image.resize(resize_to, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error loading image: {str(e)}")
        return None

def add_rounded_corners(image, radius):
    """
    Add rounded corners to a PIL image.

    Args:
        image (PIL.Image.Image): The original image.
        radius (int): Radius of the rounded corners.

    Returns:
        PIL.Image.Image: Image with rounded corners.
    """
    try:
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
        rounded = Image.new("RGBA", image.size)
        rounded.paste(image, (0, 0), mask)
        return rounded
    except Exception as e:
        print(f"Error adding rounded corners: {str(e)}")
        return image  # fallback
