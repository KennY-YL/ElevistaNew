import os
import shutil
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import pickle
from io import BytesIO
import urllib.request
from utils.utils import clear_content,custom_input_dialog
from firebase_service import firebase_service  # Import the instance, NOT class
from constants import SURVEY_DIR,FOLDER_IMAGE
from auth import auth_manager # User login info

# Initialize Firebase only once (you should call it early, like in app.py, not here)
# firebase_service.initialize()   # REMOVE this from here to avoid multiple initialize

def open_survey_folder_window(content_container):
    """Display the survey folder window."""
    global scrollable_frame, survey_frame,content  # Declare global to modify
    content = content_container
    clear_content(content_container)

    # --- Main Survey Frame ---
    survey_frame = ctk.CTkFrame(content_container, fg_color="#e5e5e5")
    survey_frame.pack(fill="both", expand=True)

    # --- Add Folder Frame (Top section) ---
    add_folder_frame = ctk.CTkFrame(
        survey_frame, fg_color="#d3d3d3", height=100, corner_radius=0, width=1200
    )
    add_folder_frame.pack(fill="x", pady=10)
    add_folder_frame.pack_propagate(False)

    # Plus (+) Button
    plus_btn = ctk.CTkButton(
        add_folder_frame, text="+", font=("Poppins", 28, "bold"),
        width=50, height=50, fg_color="white", text_color="black",
        hover_color="#bfbfbf", corner_radius=10,
        command=add_survey
    )
    plus_btn.pack(side="left", padx=20, pady=10)

    # "Add new survey folder" Label as a Button
    add_folder_label = ctk.CTkButton(
        add_folder_frame, text="Add new survey folder", font=("Poppins", 18, "bold"),
        fg_color="#d3d3d3", text_color="black", hover_color="#bfbfbf",
        border_width=0, corner_radius=10,
        command=add_survey
    )
    add_folder_label.pack(side="left", padx=10)

    # --- Survey Folder Scrollable Section ---
    survey_folder_frame = ctk.CTkFrame(survey_frame, fg_color="#e5e5e5")
    survey_folder_frame.pack(fill="both", expand=True)

    # Canvas and Scrollbar setup
    canvas = tk.Canvas(survey_folder_frame, bg="#e5e5e5", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(survey_folder_frame, orientation="vertical", command=canvas.yview)
    
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#e5e5e5")
    frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Dynamic width adjustment
    def update_frame_width(event):
        canvas_width = event.width
        scrollable_frame.configure(width=canvas_width)
        canvas.itemconfig(frame_window, width=canvas_width)

    canvas.bind("<Configure>", update_frame_width)

    # Enable scrolling
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- Load surveys based on login state ---
    if auth_manager.is_logged_in:
        fetch_survey_folders_from_firebase(scrollable_frame)
    else:
        load_existing_surveys(scrollable_frame)

def add_survey(parent_frame):
    """Add a new survey folder, either in Firebase or locally."""
    folder_name = custom_input_dialog()
    if not folder_name:
        return
    try:
        if auth_manager.is_logged_in:
            # Use FirebaseService to check for existing folder
            if firebase_service.get_survey_folders(auth_manager.logged_in_email):
                messagebox.showerror(
                    "Error", 
                    f"A folder with the name '{folder_name}' already exists in Firebase."
                )
                return

            # Use FirebaseService to create the folder
            firebase_service.create_survey_folder(auth_manager.logged_in_email, folder_name)

            messagebox.showinfo(
                "Survey", 
                f"Folder '{folder_name}' created successfully in Firebase!",
                parent=survey_frame
            )
        else:
            folder_path = os.path.join(SURVEY_DIR, folder_name)
            if os.path.exists(folder_path):
                messagebox.showerror(
                    "Error", 
                    f"A folder with the name '{folder_name}' already exists locally."
                )
                return

            os.makedirs(folder_path, exist_ok=True)

            messagebox.showinfo(
                "Survey", 
                f"Folder '{folder_name}' created successfully locally!",
                parent=survey_frame
            )

        display_folder(folder_name)
    except Exception as e:
        messagebox.showerror("Error", f"Could not create folder:\n{str(e)}")

def fetch_survey_folders_from_firebase(parent_frame):
    """Fetch survey folders from Firestore if the user is logged in."""
    
    if auth_manager.is_logged_in:
        try:
            print(f"Fetching folders for user: {auth_manager.logged_in_email}")  # Debugging print
            # Use FirebaseService to fetch survey folders
            folders = firebase_service.get_survey_folders(auth_manager.logged_in_email)

            # Display the fetched survey folders
            for folder in folders:
                folder_name = folder.get("folder_name", "Unknown")
                print(f"Found folder: {folder_name}")  # Debugging print
                display_folder(folder_name)  # Display folder in the UI

        except Exception as e:
            print(f"Error fetching folders: {str(e)}")  # Print the error for debugging
            messagebox.showerror("Error", f"Could not fetch survey folders from Firestore:\n{str(e)}")
    else:
        # If not logged in, load local surveys
        load_existing_surveys(parent_frame)



def load_existing_surveys(parent_frame):
    """Load and display existing local survey folders."""
    if not os.path.exists(SURVEY_DIR):
        os.makedirs(SURVEY_DIR)

    folders = [f for f in os.listdir(SURVEY_DIR) if os.path.isdir(os.path.join(SURVEY_DIR, f))]
    for folder_name in folders:
        display_folder(parent_frame, folder_name)


def parse_survey_file(file_path):
    """Extracts Date, Location, Description, Metrics, Image Path, and Timestamp from a pickle survey file."""
    # Default survey details
    default_details = {
        "Date": "Unknown",
        "Location": "Unknown",
        "Description": "No description available.",
        "Metrics": {
            "Horizontal Distance": "N/A",
            "Vertical Angle": "N/A",
            "Slope": "N/A",
            "Elevation": "N/A"
        },
        "Image Path": "N/A",
        "Timestamp": "N/A"
    }

    try:
        # Load the pickle file
        with open(file_path, "rb") as file:
            survey_data = pickle.load(file)

        # Extract data with fallback to default if not found
        details = default_details.copy()

        details["Date"] = survey_data.get("date", details["Date"])
        details["Location"] = survey_data.get("location", details["Location"])
        details["Description"] = survey_data.get("description", details["Description"])

        # Extract metrics, falling back to default values for each metric
        metrics = survey_data.get("metrics", {})
        for key in details["Metrics"]:
            details["Metrics"][key] = metrics.get(key, details["Metrics"][key])

        details["Image Path"] = survey_data.get("image_path", details["Image Path"])
        details["Timestamp"] = survey_data.get("timestamp", details["Timestamp"])

    except Exception as e:
        print(f"Error reading pickle file {file_path}: {e}")

    return details
def load_and_display_image(image_url, label):
    """Fetch image URL and display it in the Tkinter label."""
    try:
        print(f"Fetching image from URL: {image_url}")
        
        # Step 1: Fetch the image data using urllib
        with urllib.request.urlopen(image_url) as response:
            img_data = response.read()  # Read image data from the URL
            
            # Step 2: Check if the response is indeed an image by looking at the content type
            if 'image' not in response.getheader('Content-Type'):
                print("The URL does not return an image")
                return

            # Step 3: Open image using PIL
            img_pil = Image.open(BytesIO(img_data)).resize((250, 250), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img_pil)  # Use ImageTk.PhotoImage for Tkinter compatibility
            
            # Step 4: Display the image in the label
            label.configure(image=img)
            label.image = img  # Keep a reference to avoid garbage collection
            print("Image loaded successfully")
        
    except Exception as e:
        print(f"Error loading image: {e}")

def display_fetched_surveys(surveys, scrollable_frames):
    """Display fetched surveys in the scrollable frame."""
    if not surveys:
        empty_label = ctk.CTkLabel(scrollable_frames, text="No surveys found.", font=("Poppins", 16, "italic"))
        empty_label.pack(pady=10)
        return

    for survey in surveys:
        file_frame = ctk.CTkFrame(scrollable_frames, fg_color="white", corner_radius=10)
        file_frame.pack(fill="x", padx=10, pady=8)

        # Top header row with title, date, and menu button
        header_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        survey_title = ctk.CTkLabel(header_frame, text="Survey", font=("Poppins", 20, "bold"))
        survey_title.pack(side="left", anchor="w")

        menu_btn = ctk.CTkButton(header_frame, text="⋮", width=30, fg_color="white", text_color="black", corner_radius=5)
                                #  command=menu_button_dialog)
        menu_btn.pack(side="right")

        # Content area (address, datetime, image, description, and metrics)
        content_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)

        # Ensure 5 columns for alignment
        for col in range(5):
            content_frame.grid_columnconfigure(col, weight=1)

        # Address section (location label)
        address_label = ctk.CTkLabel(content_frame, text="Address", font=("Poppins", 12))
        address_label.grid(row=0, column=1, sticky="w", padx=10)

        location_label = ctk.CTkLabel(content_frame, text=survey["location"], font=("Poppins", 16, "bold", "italic"))
        location_label.grid(row=1, column=1, sticky="w", padx=10)

        # Date and Time section
        datetime_label = ctk.CTkLabel(content_frame, text="Date and Time", font=("Poppins", 12))
        datetime_label.grid(row=0, column=3, sticky="w", padx=10)

        datetime_value = ctk.CTkLabel(content_frame, text=survey["date"], font=("Poppins", 16, "bold", "italic"))
        datetime_value.grid(row=1, column=3, sticky="w", padx=10)

        # Image section
        image_label = ctk.CTkLabel(content_frame, text="")  # Label to hold the image
        image_label.grid(row=0, column=0, rowspan=4, padx=10, sticky="n")

        image_drive_id = survey.get("image_drive_id")
        if image_drive_id:
            image_url = f"https://drive.google.com/uc?id={image_drive_id}"
            load_and_display_image(image_url, image_label)  # Display the image

        # Description section
        desc_label = ctk.CTkLabel(content_frame, text="Description:", font=("Poppins", 11, "bold"))
        desc_label.grid(row=2, column=1, sticky="w", padx=(10, 2))

        desc_text = ctk.CTkLabel(content_frame, text=survey["description"], font=("Poppins", 11), anchor="w")
        desc_text.grid(row=2, column=2, columnspan=3, sticky="ew")

        # Metrics section (Elevation, Slope, Horizontal Distance, Vertical Angle)
        metrics = survey.get("metrics", {})
        metric_labels = [
            ("Elevation:", metrics.get("Elevation", "N/A")),
            ("Slope:", metrics.get("Slope", "N/A")),
            ("Horizontal Distance:", metrics.get("Horizontal Distance", "N/A")),
            ("Vertical Angle:", metrics.get("Vertical Angle", "N/A"))
        ]

        # Display metrics in two rows: first row for Elevation and Slope, second for Horizontal Distance and Vertical Angle
        for idx, (label, value) in enumerate(metric_labels):
            row = 3 + (idx // 2)  # Start from row 3 and adjust for two metrics per row
            col = (idx % 2) * 2 + 1  # Column 1 or 3 based on the index

            label_widget = ctk.CTkLabel(content_frame, text=label, font=("Poppins", 11, "bold"))
            label_widget.grid(row=row, column=col, sticky="w", padx=10)

            value_widget = ctk.CTkLabel(content_frame, text=value, font=("Poppins", 11))
            value_widget.grid(row=row, column=col + 1, sticky="w")

def view_survey_files(parent_frame,folder_name):
    """Displays all text files in the selected folder dynamically."""

    clear_content(content)

    view_survey_files_frame = ctk.CTkFrame(content, fg_color="#e5e5e5")
    view_survey_files_frame.pack(fill="both", expand=True)

    # Create canvas and scrollbar
    canvas = ctk.CTkCanvas(view_survey_files_frame, bg="#e5e5e5", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(view_survey_files_frame, orientation="vertical", command=canvas.yview)

    # Scrollable frame inside the canvas
    scrollable_frames = ctk.CTkFrame(canvas, fg_color="#e5e5e5")

    # Update frame width on canvas resize
    def update_frame_width(event):
        canvas_width = event.width
        scrollable_frames.configure(width=canvas_width)
        canvas.itemconfig(frame_window, width=canvas_width)

    canvas.bind("<Configure>", update_frame_width)

    # Create a window inside the canvas for scrollable frame
    frame_window = canvas.create_window((0, 0), window=scrollable_frames, anchor="nw")
    scrollable_frames.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if auth_manager.is_logged_in:
        # Fetch survey details from Firestore using FirebaseService
        try:
            # Get user's survey folders
            folders = firebase_service.get_survey_folders(auth_manager.logged_in_email)

            # Check if the folder exists for the user
            folder_found = False
            for folder in folders:
                if folder["folder_name"] == folder_name:
                    folder_found = True
                    break

            if not folder_found:
                messagebox.showinfo("Info", f"No survey folder named '{folder_name}' found.")
                return

            # Fetch surveys inside the folder for the logged-in user
            surveys_ref = firebase_service.db.collection("surveys") \
                .where("folder_name", "==", folder_name) \
                .where("user_email", "==", auth_manager.logged_in_email).stream()

            surveys = [survey.to_dict() for survey in surveys_ref]

            if not surveys:
                messagebox.showinfo("Info", "No surveys found in this folder.")
            else:
                # Display the fetched surveys using a helper function
                display_fetched_surveys(surveys, scrollable_frames)

        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch survey files from Firestore:\n{str(e)}")
    else:
        # If not logged in, load local surveys
        folder_path = os.path.join(SURVEY_DIR, folder_name)
        files = [f for f in os.listdir(folder_path) if f.endswith(".pkl")]
        
        if not files:
            empty_label = ctk.CTkLabel(scrollable_frames, text="No text files found.", font=("Poppins", 16, "italic"))
            empty_label.pack(pady=10)

        for index, file in enumerate(files, start=1):
            file_path = os.path.join(folder_path, file)
            survey_details = parse_survey_file(file_path)

            # Main frame per survey
            file_frame = ctk.CTkFrame(scrollable_frames, fg_color="white", corner_radius=10)
            file_frame.pack(fill="x", padx=10, pady=8)

            # Header section with title, date, and menu button
            header_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            survey_title = ctk.CTkLabel(header_frame, text=f"Survey {index}", font=("Poppins", 20, "bold"))
            survey_title.pack(side="left", anchor="w")

            menu_btn = ctk.CTkButton(header_frame, text="⋮", width=30, fg_color="white", text_color="black", corner_radius=5)
                                    #   command=menu_button_dialog)
            menu_btn.pack(side="right")

            # Content area (address, datetime, image, and metrics)
            content_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=10)

            for col in range(5):
                content_frame.grid_columnconfigure(col, weight=1)

            # Address
            address_label = ctk.CTkLabel(content_frame, text="Address", font=("Poppins", 12))
            address_label.grid(row=0, column=1, sticky="w", padx=10)

            location_label = ctk.CTkLabel(content_frame, text=survey_details["Location"], font=("Poppins", 16, "bold", "italic"))
            location_label.grid(row=1, column=1, sticky="w", padx=10)

            # Date and Time
            datetime_label = ctk.CTkLabel(content_frame, text="Date and Time", font=("Poppins", 12))
            datetime_label.grid(row=0, column=3, sticky="w", padx=10)

            datetime_value = ctk.CTkLabel(content_frame, text=survey_details["Date"], font=("Poppins", 16, "bold", "italic"))
            datetime_value.grid(row=1, column=3, sticky="w", padx=10)

            # Image
            # Image loading and handling
            image_path = survey_details.get("Image Path", FOLDER_IMAGE)  # Use FOLDER_IMAGE as default

            try:
                image_pil = Image.open(image_path).resize((250, 250), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Failed to load image {image_path}: {e}")
                image_pil = Image.open(FOLDER_IMAGE).resize((250, 250), Image.Resampling.LANCZOS)

            image = ImageTk.PhotoImage(image_pil)
            image_label = ctk.CTkLabel(content_frame, image=image, text="")
            image_label.image = image  # Keep a reference to the image to prevent garbage collection
            image_label.grid(row=0, column=0, rowspan=4, padx=10, sticky="n")

            # Description
            desc_label = ctk.CTkLabel(content_frame, text="Description:", font=("Poppins", 11, "bold"))
            desc_label.grid(row=2, column=1, sticky="w", padx=(10, 2))

            desc_text = ctk.CTkLabel(content_frame, text=survey_details["Description"], font=("Poppins", 11), anchor="w")
            desc_text.grid(row=2, column=2, columnspan=3, sticky="ew")

            # Metrics
            metrics = survey_details["Metrics"]
            metric_labels = [
                ("Elevation :", metrics.get("Elevation", "N/A")),
                ("Slope:", metrics.get("Slope", "N/A")),
                ("Horizontal Distance:", metrics.get("Horizontal Distance", "N/A")),
                ("Vertical Angle:", metrics.get("Vertical Angle", "N/A"))
            ]

            # Metrics display in two rows
            for idx, (label, value) in enumerate(metric_labels[:2]):
                label_widget = ctk.CTkLabel(content_frame, text=label, font=("Poppins", 11, "bold"))
                label_widget.grid(row=3, column=1 + idx, sticky="w", padx=10)

                value_widget = ctk.CTkLabel(content_frame, text=value, font=("Poppins", 11))
                value_widget.grid(row=3, column=2 + idx, sticky="w")

            for idx, (label, value) in enumerate(metric_labels[2:], start=4):
                label_widget = ctk.CTkLabel(content_frame, text=label, font=("Poppins", 11, "bold"))
                label_widget.grid(row=idx, column=1, sticky="w", padx=10)

                value_widget = ctk.CTkLabel(content_frame, text=value, font=("Poppins", 11))
                value_widget.grid(row=idx, column=2, sticky="w")

def display_folder(parent_frame,folder_name):
    # global scrollable_frame
    """Displays a folder in the survey window."""

    folder_path = os.path.join(SURVEY_DIR, folder_name)

    # Create Folder Display Frame
    folder_frame = tk.Frame(parent_frame, bg="#d3d3d3", padx=10, pady=5, height=200)
    folder_frame.pack(fill="x", pady=5)
    folder_frame.pack_propagate(False)

    # Load and display the folder image
    image_path = FOLDER_IMAGE
    image = ImageTk.PhotoImage(Image.open(image_path).resize((150, 150), Image.Resampling.LANCZOS))

    image_label = ctk.CTkLabel(folder_frame, image=image, text="")
    image_label.image = image
    image_label.pack(side="left", padx=10)

    # Folder Info Section
    folder_info_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    folder_info_frame.pack(side="left", padx=10)

    folder_label = ctk.CTkLabel(folder_info_frame, text=folder_name, font=("Poppins", 16, "bold"))
    folder_label.grid(row=0, column=0, sticky="w")

    edit_label = ctk.CTkLabel(folder_info_frame, text="edit", font=("Poppins", 14, "underline"), cursor="hand2")
    edit_label.grid(row=0, column=1, sticky="w")

    # Buttons Section
    button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    button_frame.pack(side="bottom", anchor="se", padx=10, pady=10)

    view_btn = ctk.CTkButton(button_frame, text="View", font=("Poppins", 14, "bold"), fg_color="#18a999", text_color="white", corner_radius=5,
                             command=lambda: view_survey_files(parent_frame,folder_name))  # Pass folder name to view function
    view_btn.pack(side="left", padx=5)

    delete_btn = ctk.CTkButton(button_frame, text="Delete", font=("Poppins", 14, "bold"), fg_color="#ff5252", text_color="white", corner_radius=5,
                               command=lambda: delete_survey(folder_frame, folder_path, folder_name))
    delete_btn.pack(side="left", padx=5)




def delete_survey(folder_widget, folder_path, folder_name):
    try:
        if auth_manager.is_logged_in:
            # If logged in, delete the survey and folder entries in Firestore
            # Delete surveys associated with the folder
            firebase_service.delete_surveys_in_folder(auth_manager.logged_in_email, folder_name)
            
            # Delete the folder entry itself
            firebase_service.delete_survey_folder(auth_manager.logged_in_email, folder_name)

        else:
            # If not logged in, delete the folder locally
            shutil.rmtree(folder_path)  # Recursively delete the folder and its contents
            messagebox.showinfo("Deleted", "Folder deleted successfully!")

        folder_widget.destroy()  # Remove from UI
        open_survey_folder_window()

    except Exception as e:
        messagebox.showerror("Error", f"Could not delete folder:\n{str(e)}")


