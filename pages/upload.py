import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from utils.utils import clear_content
from constants import SURVEY_DIR
import pickle

def upload_file(content_container):
    """Open file dialog, display selected image, and show form to submit survey."""
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )
    
    if not file_path:
        return  # User cancelled

    clear_content(content_container)

    upload_frame = ctk.CTkFrame(content_container, fg_color="#e5e5e5")
    upload_frame.pack(fill="both", expand=True)

    # Variables for form inputs
    title_var = tk.StringVar()
    desc_var = tk.StringVar()
    phone_var = tk.StringVar(value="Android")

    # Function to enable/disable submit button
    def validate_fields(*args):
        if title_var.get().strip() and desc_var.get().strip() and phone_var.get():
            submit_button.configure(state="normal")
        else:
            submit_button.configure(state="disabled")

    title_var.trace_add("write", validate_fields)
    desc_var.trace_add("write", validate_fields)
    phone_var.trace_add("write", validate_fields)

    # Left Image Frame
    image_frame = ctk.CTkFrame(upload_frame, width=500, height=500, fg_color="white")
    image_frame.pack(side="left", padx=50, pady=50)
    image_frame.pack_propagate(False)

    img = Image.open(file_path).resize((500, 500), Image.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 500))
    img_label = ctk.CTkLabel(image_frame, image=ctk_img, text="")
    img_label.pack(expand=True, fill="both")

    # Right Form Frame
    form_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
    form_frame.pack(side="right", padx=50, pady=50, fill="both", expand=True)

    survey_label = ctk.CTkLabel(form_frame, text="New Survey", font=("Poppins", 25, "bold"), text_color="black")
    survey_label.pack(anchor="w", pady=(0, 20))

    # Survey Title
    ctk.CTkLabel(form_frame, text="Survey Title", text_color="black").pack(anchor="w")
    title_entry = ctk.CTkEntry(form_frame, width=400, textvariable=title_var)
    title_entry.pack(pady=(0, 15))

    # Description
    ctk.CTkLabel(form_frame, text="Description", text_color="black").pack(anchor="w")
    desc_entry = ctk.CTkEntry(form_frame, width=400, textvariable=desc_var)
    desc_entry.pack(pady=(0, 15))

    # Phone Selection
    ctk.CTkLabel(form_frame, text="Phone Used", text_color="black").pack(anchor="w")
    phone_dropdown = ctk.CTkOptionMenu(
        form_frame, values=["Android", "iPhone", "Other"], width=400,
        variable=phone_var
    )
    phone_dropdown.pack(pady=(0, 20))

    # Submit Button
    submit_button = ctk.CTkButton(
        form_frame, text="Submit", fg_color="#09AAA3", hover_color="#07A293",
        text_color="white", width=200, height=40, state="disabled",
        command=lambda: submit_survey(title_var.get(), desc_var.get(), phone_var.get(), file_path)
    )
    submit_button.pack(pady=20)

def submit_survey(title, description, phone_used, image_path):
    """Save the survey data locally."""
    if not title or not description or not phone_used:
        messagebox.showerror("Error", "All fields are required.")
        return

    survey_data = {
        "title": title,
        "description": description,
        "phone_used": phone_used,
        "image_path": image_path,
    }

    try:
        if not os.path.exists(SURVEY_DIR):
            os.makedirs(SURVEY_DIR)

        file_name = f"{title.replace(' ', '_')}.pkl"
        save_path = os.path.join(SURVEY_DIR, file_name)

        with open(save_path, "wb") as f:
            pickle.dump(survey_data, f)

        messagebox.showinfo("Success", f"Survey '{title}' saved successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to save survey:\n{str(e)}")
