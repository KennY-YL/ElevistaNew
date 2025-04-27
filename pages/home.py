import customtkinter as ctk
from PIL import Image, ImageTk
from utils.utils import clear_content
from constants import WIDTH, HEIGHT
import os

def show_home(content_container):
    """Display the Home page content."""
    clear_content(content_container)

    # --- Main home frame ---
    home_frame = ctk.CTkFrame(content_container, fg_color="#0a0a23")
    home_frame.pack(fill="both", expand=True)

    # Load background image
    bg_image_path = os.path.join("assets", "images", "HomeBackground.png")
    bg_photo = None
    if os.path.exists(bg_image_path):
        bg_image = Image.open(bg_image_path).resize((WIDTH, HEIGHT), Image.LANCZOS)
        bg_photo = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(WIDTH, HEIGHT))
    else:
        print(f"Background image not found at {bg_image_path}")

    # --- Canvas for scrollable content ---
    canvas = ctk.CTkCanvas(home_frame, width=WIDTH, height=HEIGHT)
    scrollbar = ctk.CTkScrollbar(home_frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Background image
    if bg_photo:
        image_label = ctk.CTkLabel(scrollable_frame, image=bg_photo, text="", fg_color="transparent")
        image_label.image = bg_photo
        image_label.pack()

    # --- Section starts ---
    section = ctk.CTkFrame(scrollable_frame, fg_color="#3E3E3E")
    section.pack(padx=0, pady=0, fill="both", expand=True)

    # Header
    ctk.CTkLabel(section, text="TOPOGRAPHIC SURVEYING", font=("Inter", 50, "bold"),
                 text_color="#00BCD4", fg_color="transparent").pack(pady=(20, 25), padx=20, fill="x")

    # --- Introduction ---
    cta_frame = ctk.CTkFrame(section, fg_color="transparent")
    cta_frame.pack(anchor="w", padx=30, pady=(10, 20), fill="both")

    content_frame = ctk.CTkFrame(cta_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True)

    # Texts
    text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    text_frame.pack(side="left", fill="both", expand=True, anchor="n")

    texts = [
        ("What is Topographic Surveying?", ("Inter", 40, "bold"), "#00BCD4"),
        ("Topographic surveying is the process of measuring and mapping the elevation of land", 
        ("Inter", 20), "#FFFFFF"),
        ("surfaces to determine variations in terrain height. It involves collecting data on natural and ", 
        ("Inter", 20), "#FFFFFF"),
        ("artificial features to create contour maps or digital elevation models.", 
        ("Inter", 20), "#FFFFFF")
    ]

    for text, font, color in texts:
        ctk.CTkLabel(text_frame, text=text, font=font, text_color=color, wraplength=820, justify="left").pack(anchor="w", pady=7)

    # Image
    topo_image_path = os.path.join("assets", "images", "Topographic.png")
    if os.path.exists(topo_image_path):
        photo = ImageTk.PhotoImage(Image.open(topo_image_path).resize((300, 290), Image.LANCZOS))
        ctk.CTkLabel(content_frame, image=photo, text="").pack(side="right", padx=(0, 150), anchor="n")

    # --- Key Parameters ---
    ctk.CTkLabel(section, text="Key Parameters", font=("Inter", 40, "bold"), text_color="#00BCD4").pack(anchor="w", padx=30, pady=(10, 10))

    parameters = {
        "Horizontal Distance": "The straight-line distance between two points on the land surface.",
        "Vertical Distance": "The difference in height between two points.",
        "Vertical Angle": "The angle from a horizontal reference line to a point above/below.",
        "Elevation": "The height relative to a reference level (usually sea level).",
        "Slope": "Rate of elevation change over distance, expressed as % or ratio."
    }

    card_container = ctk.CTkFrame(section, fg_color="transparent")
    card_container.pack(padx=30, pady=30)

    for index, (title, desc) in enumerate(parameters.items()):
        row, col = divmod(index, 3)
        card = ctk.CTkFrame(card_container, width=300, height=150, corner_radius=10)
        card.grid(row=row, column=col, padx=25, pady=20, sticky="n")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(inner, text=title, font=("Inter", 16, "bold"), text_color="#000000").pack(anchor="w", pady=(30,0))
        ctk.CTkLabel(inner, text=desc, font=("Inter", 13), text_color="#444444", wraplength=260, justify="left").pack(anchor="w", pady=(10,0))

    # --- Calculations Section ---
    ctk.CTkLabel(section, text="Calculations", font=("Inter", 40, "bold"), text_color="#00BCD4").pack(anchor="w", padx=30, pady=(20, 10))

    formulas = [
        ("Vertical Distance", "V = elev + r - hi"),
        ("Vertical Angle", "VA = ArcTan(hi / H)"),
        ("Slope", "Slope = V / H")
    ]

    formula_container = ctk.CTkFrame(section, fg_color="transparent")
    formula_container.pack(padx=30, pady=(0, 20))

    for index, (title, formula) in enumerate(formulas):
        row, col = divmod(index, 3)
        card = ctk.CTkFrame(formula_container, width=260, height=110, corner_radius=10)
        card.grid(row=row, column=col, padx=20, pady=10)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(inner, text=title, font=("Inter", 18, "bold"), text_color="#000000").pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(inner, text=formula, font=("Inter", 16), text_color="#444444").pack(anchor="center")

    # --- Variables Legend ---
    ctk.CTkLabel(section, text="Variables Legend", font=("Inter", 40, "bold"), text_color="#00BCD4").pack(anchor="w", padx=30, pady=(0, 20))

    legend = {
        "V": "Vertical Distance",
        "VA": "Vertical Angle",
        "hi": "Height of the instrument",
        "r": "Height of object of reference",
        "elev": "Elevation",
        "H": "Horizontal Distance"
    }

    legend_card = ctk.CTkFrame(section, fg_color="#FFFFFF", corner_radius=10)
    legend_card.pack(padx=35, pady=(0, 20))

    legend_container = ctk.CTkFrame(legend_card, fg_color="transparent")
    legend_container.pack(padx=30, pady=20)

    for i, (symbol, meaning) in enumerate(legend.items()):
        row, col = divmod(i, 2)
        cell = ctk.CTkFrame(legend_container, fg_color="transparent")
        cell.grid(row=row, column=col, padx=40, pady=5, sticky="w")
        ctk.CTkLabel(cell, text=symbol, font=("Inter", 14, "bold"), text_color="#00BCD4", width=40).pack(side="left")
        ctk.CTkLabel(cell, text=meaning, font=("Inter", 14), text_color="#000000").pack(side="left")

    # Note
    ctk.CTkLabel(section, text="Note:", font=("Inter", 14, "bold"), text_color="#00BCD4").pack(anchor="w", padx=30, pady=(10, 5))
    ctk.CTkLabel(section, text="Elevation and Horizontal distance are estimated by the trained AI model.",
                 font=("Inter", 13), text_color="#FFFFFF", wraplength=800, justify="left").pack(anchor="w", padx=30, pady=(0, 30))

    # --- Footer + Upload Button ---
    ctk.CTkLabel(scrollable_frame, text="© 2025 Topographic Surveying. All rights reserved.\nLast updated: April 24, 2025",
                 font=("Inter", 12), text_color="#AAAAAA", fg_color="transparent").pack(pady=20)

    upload_btn = ctk.CTkButton(
        scrollable_frame, text="UPLOAD", font=("Poppins", 25, "bold"),
        fg_color="#09AAA3", text_color="white", width=200, height=48,
        # command=upload_callback
    )
    upload_btn.place(relx=0.5, rely=0.18, anchor="center")
