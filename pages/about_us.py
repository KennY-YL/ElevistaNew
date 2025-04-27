import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from utils.utils import clear_content
import os
from constants import REGIENA_IMAGE, CHANTEL_IMAGE, JHON_IMAGE
from utils.image_helpers import insert_circular_image


def show_about_us(content_container):
    """Display the About Us page."""
    clear_content(content_container)

    about_frame = ctk.CTkFrame(content_container, fg_color="#e5e5e5")
    about_frame.pack(fill="both", expand=True)

    about_label = ctk.CTkLabel(
        about_frame,
        text="About EleVista",
        font=("Poppins", 35, "bold")
    )
    about_label.pack(anchor="w", pady=(20, 5), padx=(75, 5))

    description = (
        "EleVista was developed to bridge the gap between traditional surveying "
        "and the cutting-edge power of AI, making land elevation measurement smarter, faster, and more accessible."
    )
    desc_label = ctk.CTkLabel(
        about_frame,
        text=description,
        wraplength=900,
        justify="center",
        font=("Poppins", 20)
    )
    desc_label.pack(pady=(20, 20))

    team_label = ctk.CTkLabel(
        about_frame,
        text="MEET THE TEAM",
        font=("Poppins", 25, "bold")
    )
    team_label.pack(pady=(20, 0))

    members = [
        ("REGIENA MAE E. CABALLES", "CPE - 4201", REGIENA_IMAGE),
        ("CHANTEL KYLIE M. MALUNDAS", "CPE - 4201", CHANTEL_IMAGE),
        ("JHON KENNETH M. YLAGAN", "CPE - 4201", JHON_IMAGE)
    ]

    container_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
    container_frame.pack(pady=(20, 40))

    for name, title, image_path in members:
        member_frame = ctk.CTkFrame(
            container_frame,
            width=250,
            height=300,
            fg_color="#D9D9D9"
        )
        member_frame.pack(side="left", padx=(20, 20))
        member_frame.pack_propagate(False)

        circle_canvas = ctk.CTkCanvas(
            member_frame,
            width=300,
            height=300,
            bg="#D9D9D9",
            highlightthickness=0
        )
        circle_canvas.create_oval(10, 10, 290, 290, outline="#0C2C44", width=2)
        circle_canvas.pack(pady=20)

        insert_circular_image(circle_canvas, image_path)

        name_label = ctk.CTkLabel(
            member_frame,
            text=name,
            font=("Poppins", 15, "bold")
        )
        name_label.pack()

        title_label = ctk.CTkLabel(
            member_frame,
            text=title,
            font=("Poppins", 14)
        )
        title_label.pack()

