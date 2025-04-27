import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from utils.utils import clear_content
from constants import IMAGE_FILES
from utils.image_helpers import add_rounded_corners

def open_instruction_window(content_container):
    # Clear previous content
    clear_content(content_container)

    # Create main frame
    manual_frame = ctk.CTkFrame(content_container, fg_color="#e5e5e5")
    manual_frame.pack(fill="both", expand=True)

    # Create canvas and scrollbar
    canvas = tk.Canvas(manual_frame, bg="#e5e5e5")
    scrollbar = ttk.Scrollbar(manual_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#e5e5e5")

    scrollable_frame.bind( "<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Title Section
    title_label = tk.Label(scrollable_frame, text="Instruction Manual", font=("Arial", 35, "bold"), bg="#e5e5e5")
    title_label.pack(pady=(35, 53), padx=25, anchor='w')

    # How to Collect Data Section
    collect_label = tk.Label(scrollable_frame, text="How to Collect Data", font=("Arial", 25, "bold"), bg="#e5e5e5")
    collect_label.pack(anchor="w", pady=(1, 25), padx=25)

    tools_label = tk.Label(scrollable_frame, text="-----------------------------------------------------------------------Tools You'll Need:-----------------------------------------------------------------------------", font=("Arial", 22), bg="#e5e5e5")
    tools_label.pack(anchor="w", padx=40)

    image_files = IMAGE_FILES

        # Canvas for image gallery
    img_canvas = tk.Canvas(scrollable_frame, width=1200, height=350, bg="#0C1822", highlightthickness=0, relief="flat")
    img_canvas.pack(pady=20)

        # Frame to hold images
    frame = tk.Frame(img_canvas, bg="#0C1822")
    img_canvas.create_window((0, 0), window=frame, anchor="nw")

        # Hover text label
    tooltip = tk.Label(manual_frame, text="", bg="#333333", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
    tooltip.place_forget()

    # Hover functions
    def on_hover(event, text):
        tooltip.config(text=text)
        tooltip.place(
            x=event.x_root - manual_frame.winfo_rootx() + 15,
            y=event.y_root - manual_frame.winfo_rooty() + 15
            )

    def on_leave(event):
        tooltip.place_forget()

        # Load and display images with hover effect
    images = []
    labels = []

    for i, (file, hover_text) in enumerate(image_files):
        img = Image.open(file)
        img = img.resize((270, 315), Image.LANCZOS)

        img_rounded = add_rounded_corners(img, radius=40)

        img_tk = ImageTk.PhotoImage(img_rounded)
        images.append(img_tk)

        lbl = tk.Label(frame, image=img_tk, bg="#0C1822", relief="flat", bd=0)
        lbl.grid(row=0, column=i, padx=15, pady=10)
        labels.append(lbl)

        lbl.bind("<Enter>", lambda e, text=hover_text: on_hover(e, text))
        lbl.bind("<Leave>", on_leave)

        # Smooth scrolling functionality
    scroll_x = 0
    scroll_step = 60

    def smooth_scroll(direction):
        nonlocal scroll_x
        max_scroll = (len(images) * 285) - img_canvas.winfo_width()

        if direction == "left" and scroll_x < 0:
            scroll_x += scroll_step
        elif direction == "right" and abs(scroll_x) < max_scroll:
            scroll_x -= scroll_step

        img_canvas.xview_moveto(-scroll_x / img_canvas.winfo_width())

        # Navigation buttons
    btn_left = ctk.CTkButton(
            scrollable_frame, text="❮",
            command=lambda: smooth_scroll("left"),
            fg_color="#333333", hover_color="#555555",
            text_color="white",
            width=5, height=250,
            corner_radius=10, font=("Helvetica", 18, "bold")
        )
    btn_left.place(x=170, y=180)
    

    btn_right = ctk.CTkButton(
            scrollable_frame, text="❯",
            command=lambda: smooth_scroll("right"),
            fg_color="#333333", hover_color="#555555",
            text_color="white",
            width=5, height=250,
            corner_radius=10, font=("Helvetica", 18, "bold")
        )
    btn_right.place(x=1001, y=180)

    # Update canvas scroll region
    frame.update_idletasks()
    img_canvas.config(scrollregion=img_canvas.bbox("all"))

    # Steps for Data Gathering
    steps_label = tk.Label(scrollable_frame, text="Steps for Data Gathering", font=("Arial", 25, "bold"), bg="#e5e5e5")
    steps_label.pack(anchor="w", padx=20, pady=10)

    steps = [
            "Position the tripod with the mobile phone on the ground, centered in the middle of the inclined land.",
            "Ensure that the bubble level on the tripod is centered.",
            "Measure the height of the phone from the ground and ensure it is 83 cm.",
            "Adjust the tilt feature (camera level) of the phone and ensure that it is leveled at a 90-degree angle.",
            "Measure distances ranging from 2 meters to 12 meters. (Note: The model only recognizes distances up to 12 meters).",
            "Position the tripod or marker stick at the desired distance.",
            "Capture an image of the person holding the tripod or marker stick. Make sure the height of the object is visible in the picture."
        ]

    for i, step in enumerate(steps, 1):
        tk.Label(scrollable_frame, text=f"{i}. {step}", bg="#e5e5e5",font=("Arial", 16)).pack(anchor="w", padx=40, pady=2)

        # How to Use the System
    use_label = tk.Label(scrollable_frame, text="How to Use the System", font=("Arial", 16, "bold"), bg="#e5e5e5")
    use_label.pack(anchor="w", padx=20, pady=10)

    use_steps = [
            "Step 1: Import the Images - Upload images to the system.",
            "Step 2: Name the file and provide a description. (Optional)",
            "Step 3: Wait for processing. Once completed, the survey information will be displayed."
        ]

    for step in use_steps:
        tk.Label(scrollable_frame, text=step, bg="#e5e5e5",font=("Arial", 16)).pack(anchor="w", padx=40, pady=2)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
