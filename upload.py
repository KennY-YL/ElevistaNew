import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
from itertools import cycle
from tkinter import messagebox,simpledialog
import firebase_admin
from firebase_admin import credentials, firestore,storage
import hashlib  # For password hashing
import json
import os
from datetime import datetime
import shutil
import pickle
import requests
from io import BytesIO
from tkinter import PhotoImage
import os
import shutil
import pickle
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow  # For OAuth2 Flow
from google.auth.transport.requests import Request  # For refreshing tokens
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import urllib.request
# Initialize customtkinter
ctk.set_appearance_mode("white")
ctk.set_default_color_theme("blue")

# Set initial window size
WIDTH, HEIGHT = 1200, 650
ACCESS_TOKEN = "52b534ddb55a33694193dcc6549142cff8adc989"

# Keep track of all open top-level windows
open_windows = []

active_windows = {}

# Initialize Firebase
cred = credentials.Certificate("elevista-1cae7-firebase-adminsdk-fbsvc-9a5b78dc69.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

SURVEY_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Surveys")

def test_firestore_connection():
    try:
        surveys_ref = db.collection("surveys").limit(1).stream()  # Fetch a single document
        for survey in surveys_ref:
            print(f"Document ID: {survey.id}, Data: {survey.to_dict()}")
    except Exception as e:
        print(f"Error testing Firestore connection: {str(e)}")

# Call this function to test the connection
test_firestore_connection()

# Loads and displays existing survey folders
if not os.path.exists(SURVEY_DIR):
    os.makedirs(SURVEY_DIR)  # Ensure the directory exists

def close_all_windows(except_window=None):
    """Hide all windows except the specified one."""
    for name, window in active_windows.items():
        if window != except_window and window.winfo_exists():
            window.withdraw()

def insert_circular_image(canvas, image_path):
    # Open and resize the image
    image = Image.open(image_path).resize((300, 300), Image.LANCZOS)
    
    # Create a circular mask
    mask = Image.new("L", (300, 300), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 300, 300), fill=255)
    
    # Create a transparent image
    circular_image = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    circular_image.paste(image, (0, 0), mask)

    # Convert to ImageTk for displaying in canvas
    canvas.image = ImageTk.PhotoImage(circular_image)
    canvas.create_image(150, 150, image=canvas.image)

# Function to close all open top-level windows and return to main window
def go_home():
    for window in open_windows:
        if window.winfo_exists():
            window.destroy()
    open_windows.clear()
    tk_root.deiconify()
    tk_root.focus_set()
    create_navigation_bar(tk_root)


"""NAV BAR FOR THE TOP LEVEL WINDOWS"""
def create_navigation_bar(parent):
    if hasattr(parent, "header_frame") and parent.header_frame.winfo_exists():
        parent.header_frame.destroy()
    
    # Create a new header frame and pack it at the top
    parent.header_frame = tk.Frame(parent, height=70, bg="#0f0f0f")  # Use 'bg' instead of 'fg_color'
    parent.header_frame.pack(side="top", fill="x", pady=0)

    # Show "EleVista" text for top-level window, else show logo for main window
    try:
        if parent == tk_root:
            logo_image = Image.open("LOGO.png").resize((50, 50), Image.Resampling.LANCZOS)
            logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(50, 50))
            logo_label = ctk.CTkLabel(parent.header_frame, image=logo_photo, text="", fg_color="transparent")
            parent.logo_photo = logo_photo  # Prevent garbage collection
        else:
            logo_label = ctk.CTkLabel(parent.header_frame, text="EleVista", font=("Poppins", 30), fg_color="transparent", text_color="white")
    except Exception as e:
        print(f"Error loading image: {e}")
        logo_label = ctk.CTkLabel(parent.header_frame, text="Logo Not Found", font=("Poppins", 20), fg_color="transparent", text_color="white")

    logo_label.pack(side="left", padx=(30, 30))

    # Destroy old nav frame if it exists
    if hasattr(parent, "nav_frame") and parent.nav_frame.winfo_exists():
        parent.nav_frame.destroy()

    # Create new Navigation Frame
    parent.nav_frame = ctk.CTkFrame(parent.header_frame, fg_color="transparent")
    parent.nav_frame.pack(side="right", padx=20, pady=15)

    # Show Profile Button if Logged In, else show Login & Sign-Up
    nav_buttons = ["home", "surveys", "manual", "about us", "LOGIN", "SIGN UP"]

    if is_logged_in:  # If logged in, show profile and other buttons
        for text in nav_buttons:
            if text == "home":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
            elif text == "surveys":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=open_survey_folder_window)
            elif text == "manual":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
            elif text == "about us":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=about_us_window)
            btn.pack(side="left", padx=10)

        # Add profile image button
        profile_img = ctk.CTkImage(Image.open("profile.png"), size=(30, 30))
        profile_btn = ctk.CTkButton(parent.nav_frame, text="", image=profile_img, width=40, height=40,
                                    fg_color="transparent", hover_color="#09AAA3", command=show_logout)
        profile_btn.pack(side="left", padx=(10, 5))
        parent.profile_img = profile_img  # Prevent garbage collection

    else:  # If not logged in, show Login and Sign Up buttons
        for text in nav_buttons:
            if text == "home":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=go_home)
            elif text == "surveys":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=open_survey_folder_window)
            elif text == "manual":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40, command=open_instruction_window)
            elif text == "about us":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", width=120, height=40,command=about_us_window)
            elif text == "LOGIN":
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="#09AAA3", text_color="white",
                                    corner_radius=5, width=120, height=40, command=show_login_window)
            else:
                btn = ctk.CTkButton(parent.nav_frame, text=text, font=("Poppins", 20), fg_color="transparent", text_color="white",
                                    corner_radius=5, hover_color="#09AAA3", border_color="#09AAA3", border_width=2, width=120, height=40,
                                    command=show_signup_window)

            btn.pack(side="left", padx=10)

    parent.header_frame.lift()
    parent.update_idletasks()
    
"""END HERE"""

"""ABOUT US WINDOW"""
def about_us_window():   
    if "aboutUs" not in active_windows or not active_windows["aboutUs"].winfo_exists():
        # Create top-level window
        tk_root.withdraw()
        aboutUs = ctk.CTkToplevel(tk_root)
        aboutUs.title("About Us")
        aboutUs.geometry(f"{WIDTH}x{HEIGHT}")
        aboutUs.configure(bg="#e5e5e5")
        center_window(aboutUs, WIDTH, HEIGHT)
        aboutUs.resizable(False, False)
        aboutUs.overrideredirect(True)
       
        # Create Navigation Bar
        create_navigation_bar(aboutUs)

        # About Section
        about_label = ctk.CTkLabel(aboutUs, text="About EleVista", font=("Poppins", 35, "bold"))
        about_label.pack(anchor="w", pady=(20, 5), padx=(75, 5))

        description = ("EleVista was developed to bridge the gap between traditional surveying and the cutting-edge power of AI, making land elevation measurement smarter, faster, and more accessible than ever before.")
        desc_label = ctk.CTkLabel(aboutUs, text=description, wraplength=900, justify="center", font=("Poppins", 20))
        desc_label.pack(pady=(20, 20))

        # Meet The Team Section
        team_label = ctk.CTkLabel(aboutUs, text="MEET THE TEAM", font=("Poppins", 25, "bold"))
        team_label.pack(pady=(20, 0))
        
        # Team Members Data
        members = [
            ("REGIENA MAE E. CABALLES", "CPE - 4201"),
            ("CHANTEL KYLIE M. MALUNDAS", "CPE - 4201"),
            ("JHON KENNETH M. YLAGAN", "CPE - 4201")
            ]# Create Colorless Parent Frame to Center Members
        container_frame = ctk.CTkFrame(aboutUs, fg_color="transparent")
        container_frame.pack(pady=(20, 40))
        image_paths = ["2.jpg", "1.jpg", "3.jpg"]

        # Create Separate Frames for Each Member
        for (name, title), image_path in zip(members, image_paths):
            member_frame = ctk.CTkFrame(container_frame, width=250, height=300, fg_color="#D9D9D9")
            member_frame.pack(side="left", padx=(20, 20))
            member_frame.pack_propagate(False)

            # Create Circular Canvas
            circle_canvas = ctk.CTkCanvas(member_frame, width=300, height=300, bg="#D9D9D9", highlightthickness=0)
            circle_canvas.create_oval(10, 10, 290, 290, outline="#0C2C44", width=2)
            circle_canvas.pack(pady=20)

            # Insert corresponding image with transparency
            insert_circular_image(circle_canvas, image_path)

            # Display Name and Title
            name_label = ctk.CTkLabel(member_frame, text=name, font=("Poppins", 15, "bold"))
            name_label.pack()

            title_label = ctk.CTkLabel(member_frame, text=title, font=("Poppins", 14))
            title_label.pack()

        active_windows["aboutUs"] = aboutUs

    
    close_all_windows(active_windows["aboutUs"])
    active_windows["aboutUs"].deiconify()

"""END HERE"""


"""MANUAL WINDOW"""
# Function the opens manual
def open_instruction_window():
    # Create top-level window
    if "instructionWindow" not in active_windows or not active_windows["instructionWindow"].winfo_exists():
        tk_root.withdraw()
        instructionWindow = ctk.CTkToplevel(tk_root)
        instructionWindow.title("Manual")
        instructionWindow.geometry(f"{WIDTH}x{HEIGHT}")
        instructionWindow.configure(bg="#e5e5e5")
        instructionWindow.focus_set()
        center_window(instructionWindow, WIDTH, HEIGHT)
        instructionWindow.resizable(False, False)
        instructionWindow.overrideredirect(True)

        # Create Navigation Bar (implement this function as needed)
        create_navigation_bar(instructionWindow)

        # Create canvas and scrollbar
        canvas = tk.Canvas(instructionWindow, bg="#e5e5e5")
        scrollbar = ttk.Scrollbar(instructionWindow, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#e5e5e5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

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

        image_files = [
            ("im1.png", "Smartphone"),
            ("im2.png", "Tripod Stand"),
            ("im3.png", "Measuring Tape"),
            ("im4.png", "Colored Chalk"),
            ("im5.png", "Stadia Rod"),
            ("im6.png", "Meter Stick"),
            ("im7.png", "Wooden Stick")
        ]

        # Canvas for image gallery
        img_canvas = tk.Canvas(scrollable_frame, width=1200, height=350, bg="#0C1822", highlightthickness=0, relief="flat")
        img_canvas.pack(pady=20)

        # Frame to hold images
        frame = tk.Frame(img_canvas, bg="#0C1822")
        img_canvas.create_window((0, 0), window=frame, anchor="nw")

        # Function to create rounded corner images
        def add_rounded_corners(image, radius):
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            
            draw.rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
            
            rounded = Image.new("RGBA", image.size)
            rounded.paste(image, (0, 0), mask)
            
            return rounded

        # Hover text label
        tooltip = tk.Label(instructionWindow, text="", bg="#333333", fg="white", font=("Helvetica", 12, "bold"), padx=10, pady=5)
        tooltip.place_forget()

        # Hover functions
        def on_hover(event, text):
            tooltip.config(text=text)
            tooltip.place(
                x=event.x_root - instructionWindow.winfo_rootx() + 15,
                y=event.y_root - instructionWindow.winfo_rooty() + 15
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

        active_windows["instructionWindow"] = instructionWindow


    close_all_windows(active_windows["instructionWindow"])
    active_windows["instructionWindow"].deiconify()

"""LOGOUT"""
popup = None  # Global variable to track the popup window
logged_in_email = ""

def get_logged_in_email():
    """Retrieve the logged-in email from Firestore."""
    global logged_in_email
    return logged_in_email if logged_in_email else "No User Logged In"

def show_logout():
    global popup

    if popup and popup.winfo_exists():
        popup.destroy()
        popup = None
    else:
        popup = ctk.CTkToplevel(tk_root)
        popup.geometry("220x120+1500+169")
        popup.configure(fg_color="white")
        popup.overrideredirect(True)

        # Fetch the logged-in email
        user_email = get_logged_in_email()

        # Email Display
        email_label = ctk.CTkLabel(popup, text=user_email, font=("Arial", 12), text_color="black")
        email_label.pack(pady=(20, 10))

        # Logout Button
        logout_button = ctk.CTkButton(popup, text="Logout", fg_color="black", text_color="white",
                                      hover_color="gray", command=logout)
        logout_button.pack(pady=10)

def logout():
    global is_logged_in, logged_in_email

    is_logged_in = False
    logged_in_email = None

    # Destroy all top-level windows to avoid conflicts
    for window in list(active_windows.values()):
        if window.winfo_exists():
            print(f"Destroying top-level window: {window}")
            window.destroy()

    active_windows.clear()

    # Hide all top-level windows and refresh navbar
    tk_root.deiconify()
    create_navigation_bar(tk_root)
    tk_root.update()

    messagebox.showinfo("Logged Out", "You have been successfully logged out.")

"""END HERE"""


        
"""LOGIN FUNCTIONALITY"""
REMEMBER_ME_FILE = "remember_me.json"


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
# Function to save credentials
def save_credentials(email):
    with open(REMEMBER_ME_FILE, "w") as f:
        json.dump({"email": email}, f)

# Function to load saved credentials
def load_credentials():
    if os.path.exists(REMEMBER_ME_FILE):
        with open(REMEMBER_ME_FILE, "r") as f:
            data = json.load(f)
            return data.get("email", "")
    return ""
# Function to check credentials
is_logged_in = False  

def login(email_entry, password_entry, remember_var, parent_window):
    global is_logged_in, logged_in_email

    email = email_entry.get()
    password = password_entry.get()

    if not email or not password:
        messagebox.showerror("Error", "Please enter both email and password.")
        return

    hashed_password = hash_password(password)

    try:
        users_ref = db.collection("users").where("email", "==", email).stream()
        for user in users_ref:
            user_data = user.to_dict()
            if user_data["password"] == hashed_password:
                if remember_var.get():
                    save_credentials(email)

                messagebox.showinfo("Success", "Login successful!")

                # Update login state
                is_logged_in = True
                logged_in_email = email

                # Destroy all top-level windows
                for window in list(active_windows.values()):
                    if window.winfo_exists():
                        print(f"Closing window: {window}")
                        window.destroy()

                active_windows.clear()

                # Ensure the main window is visible
                tk_root.deiconify()
                tk_root.lift()
                tk_root.focus_force()

            

                # Refresh the main window's navbar
                create_navigation_bar(tk_root)
                tk_root.update()

                return

        messagebox.showerror("Error", "Invalid email or password.")

    except Exception as e:
        messagebox.showerror("Error", f"Firestore error: {str(e)}")





def close_window():
    login_window.destroy()

def show_login_window():
    global login_window, email_entry, password_entry, remember_var, toggle_button
    
    # Create the login window
    login_window = ctk.CTkToplevel(tk_root)
    login_window.title("Login")
    login_window.configure(fg_color="white")
    login_window.overrideredirect(True)
    
    # Define login window size
    window_width = 500
    window_height = 500
    
    # Make sure the window opens in the foreground
    login_window.attributes('-topmost', True)

    # Set the position and size
    login_window.geometry(f"{window_width}x{window_height}+{560}+{169}")
    
    # Remove topmost attribute after placement
    login_window.after(100, lambda: login_window.attributes('-topmost', False))
    saved_email = load_credentials()
        # Close Button (X)
    close_button = ctk.CTkButton(
        login_window, text="X", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=0, border_width=0, command=login_window.destroy
    )
    close_button.place(x=450, y=10)
    ctk.CTkLabel(login_window, text="LOGIN", font=("Poppins", 30, "bold"), text_color="#09AAA3").pack(pady=(50, 20))

    ctk.CTkLabel(login_window, text="Email", font=("Poppins", 14)).pack(anchor="w", padx=50)
    email_entry = ctk.CTkEntry(login_window, width=350, font=("Poppins", 14))
    email_entry.pack(anchor="w",pady=10,padx=52)
    email_entry.insert(0, saved_email)

    # Ensure Password Label is Visible
    password_label = ctk.CTkLabel(login_window, text="Password", font=("Poppins", 14))
    password_label.pack(anchor="w", padx=50, pady=(10, 0))  # Ensure correct placement

    # Password Entry + Eye Button Frame
    password_frame = ctk.CTkFrame(login_window, fg_color="transparent")
    password_frame.pack(pady=5)

    # Password Entry
    password_entry = ctk.CTkEntry(password_frame, width=350, font=("Poppins", 14), show="*")
    password_entry.pack(side="left", padx=(0, 5))

    # Eye Toggle Button (inside password field)
    toggle_button = ctk.CTkButton(password_frame, text="", width=30, height=30, fg_color="transparent",
                                  image=eye_closed_img, command=toggle_password)
    toggle_button.pack(side="left")

    # Remember Me Checkbox
    remember_var = tk.BooleanVar(value=bool(saved_email))
    remember_me = ctk.CTkCheckBox(login_window, text="Remember Me ?", variable=remember_var, font=("Poppins", 12))
    remember_me.pack(anchor="w", padx=50, pady=10)

    # Login Button
    login_btn = ctk.CTkButton(login_window, text="LOGIN", font=("Poppins", 14, "bold"), fg_color="#00b3b3",
                              text_color="white", width=200, height=40, command=lambda: login(email_entry, password_entry, remember_var,tk_root))
    login_btn.pack(pady=20)

    # Forgot Password Label
    forgot_label = ctk.CTkLabel(
        login_window, text="Forgot Password ?", text_color="gray",
        fg_color="transparent", font=("Poppins", 12), cursor="hand2"
    )
    forgot_label.pack()

    # Divider Line
    ctk.CTkLabel(login_window, text="_________________ or _________________", text_color="gray", 
                fg_color="transparent", font=("Poppins", 12)).pack(pady=7)


    # Signup Link
    signup_label = ctk.CTkLabel(login_window, text="Need an account? SIGN UP", text_color="#00b3b3",
                                font=("Poppins", 12, "bold"), cursor="hand2")
    signup_label.pack(pady=5)
    signup_label.bind("<Button-1>", lambda e: show_signup_window())

    login_window.focus_force()
 # Load eye images
eye_open_img = ctk.CTkImage(Image.open("view.png"), size=(25, 25))
eye_closed_img = ctk.CTkImage(Image.open("hide.png"), size=(25, 25))
def toggle_password():
    """Toggle password visibility and switch eye icon."""
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")  # Show password
        toggle_button.configure(image=eye_open_img)  # Switch to open eye image
    else:
        password_entry.configure(show="*")  # Hide password
        toggle_button.configure(image=eye_closed_img)  # Switch to closed eye image
"""END HERE"""


"""SIGN UP"""
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_signup_window():
    
    # Create the sign-up window
    signup_window = ctk.CTkToplevel(tk_root)
    signup_window.title("Sign Up")
    signup_window.configure(fg_color="white")
    signup_window.overrideredirect(True)  # Remove window decorations

     # Define login window size
    window_width = 500
    window_height = 500
    
    # Make sure the window opens in the foreground
    signup_window.attributes('-topmost', True)

    # Set the position and size
    signup_window.geometry(f"{window_width}x{window_height}+{560}+{169}")
    
    # Remove topmost attribute after placement
    signup_window.after(100, lambda: signup_window.attributes('-topmost', False))

    # Close Button (X)
    close_button = ctk.CTkButton(
        signup_window, text="X", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=0, border_width=0, command=signup_window.destroy
    )
    close_button.place(x=450, y=10)

    # Sign-Up Label
    signup_label = ctk.CTkLabel(
        signup_window, text="SIGN UP", font=("Poppins", 30, "bold"),
        text_color="#00b3b3", fg_color="transparent"
    )
    signup_label.pack(pady=(50, 20))

    # Email Label & Entry
    ctk.CTkLabel(signup_window, text="Email", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    email_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14))
    email_entry.pack(pady=5)

    # Password Label & Entry
    ctk.CTkLabel(signup_window, text="Password", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    password_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14), show="*")
    password_entry.pack(pady=5)

    # Confirm Password Label & Entry
    ctk.CTkLabel(signup_window, text="Confirm Password", fg_color="transparent", font=("Poppins", 14)).pack(anchor="w", padx=50)
    confirm_password_entry = ctk.CTkEntry(signup_window, width=400, font=("Poppins", 14), show="*")
    confirm_password_entry.pack(pady=5)

    # Sign-Up Button
    signup_btn = ctk.CTkButton(
        signup_window, text="SIGN UP", font=("Poppins", 14, "bold"),
        fg_color="#00b3b3", text_color="white", width=250, height=40,
        command=lambda: sign_up(email_entry, password_entry, confirm_password_entry)  # Pass the entry fields
    )
    signup_btn.pack(pady=20)
    # Divider Line
    ctk.CTkLabel(signup_window, text="_________________ or _________________", text_color="gray",
                 fg_color="transparent", font=("Poppins", 12)).pack(pady=5)

    # Already have an account? LOGIN
    login_label = ctk.CTkLabel(
        signup_window, text="Already a user? LOGIN", text_color="#00b3b3",
        fg_color="transparent", font=("Poppins", 12, "bold"), cursor="hand2"
    )
    login_label.pack(pady=5)
    login_label.bind("<Button-1>", lambda e: show_login_window())

    # Focus on the sign-up window
    signup_window.focus_force()

def sign_up(email_entry, password_entry, confirm_password_entry):
    email = email_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    # Validate input
    if not email or not password or not confirm_password:
        messagebox.showerror("Error", "Please fill all fields.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    # Hash the password
    hashed_password = hash_password(password)

    # Store user in Firestore
    try:
        db.collection("users").add({
            "email": email,
            "password": hashed_password  # Store hashed password
        })
        messagebox.showinfo("Success", "Account created successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Firestore error: {str(e)}")
"""END HERE"""


"""FUNCTION FOR CENTERING THE WINDOWS"""
# Function to center any window
def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update()
"""END HERE"""

"""SURVEY FOLDER"""
scrollable_frame = None 

menu_dialog = None
def menu_button_dialog():
    global menu_dialog

    if menu_dialog and menu_dialog.winfo_exists():
        menu_dialog.destroy()
        menu_dialog = None
    else:
        menu_dialog = ctk.CTkToplevel(tk_root)
        menu_dialog.geometry("220x120+1500+169")
        menu_dialog.configure(fg_color="white")
        menu_dialog.overrideredirect(True)

        # Download Button
        download_button = ctk.CTkButton(menu_dialog, text="Download", fg_color="black", text_color="white",
                                      hover_color="gray")
        download_button .pack(pady=10)


        # Delete Button
        delete_button = ctk.CTkButton(menu_dialog, text="Delete", fg_color="black", text_color="white",
                                      hover_color="gray")
        delete_button.pack(pady=10)



def custom_input_dialog():
    dialog = ctk.CTkToplevel()
    dialog.title("Survey")
   
    dialog.geometry("300x175+800+300")
    dialog.configure(fg_color="white")
    dialog.resizable(False, False)
    dialog.overrideredirect(True)

    # Close Button (Top Right)
    close_button = ctk.CTkButton(
        dialog, text="✕", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=5, border_width=0, command=dialog.destroy
    )
    close_button.place(relx=1.0, x=-10, y=10, anchor="ne")  # Positions at the top-right

    # Label
    ctk.CTkLabel(dialog, text="Enter folder name:", font=("Poppins", 14), text_color="black").pack(pady=(40, 5))

    # Entry Field
    entry = ctk.CTkEntry(dialog, font=("Poppins", 12), width=200, fg_color="white", text_color="black")
    entry.pack(pady=5)

    result = ctk.StringVar()

    def submit():
        result.set(entry.get())
        dialog.destroy()

    # OK Button (Bottom Right)
    submit_button = ctk.CTkButton(
        dialog, text="OK", command=submit, font=("Arial", 14, "bold"),
        fg_color="#00b3b3", text_color="white", corner_radius=5, width=70, height=30
    )
    submit_button.place(relx=1.0, rely=1.0, x=-15, y=-15, anchor="se")  # Bottom right positioning

    dialog.grab_set()  # Make modal
    dialog.wait_window()  # Wait until closed

    return result.get()


def open_survey_folder_window():
    global scrollable_frame, surveyFolder  # Declare it as global to modify it

    # Check if the surveyFolder window is already open
    if "surveyFolder" in active_windows and active_windows["surveyFolder"].winfo_exists():
        # If it exists, destroy it to refresh
        active_windows["surveyFolder"].destroy()

    # Create a new surveyFolder window
    tk_root.withdraw()
    surveyFolder = ctk.CTkToplevel(tk_root)
    surveyFolder.title("Survey Folder")
    surveyFolder.geometry(f"{WIDTH}x{HEIGHT}")
    surveyFolder.configure(bg="#e5e5e5")
    center_window(surveyFolder, WIDTH, HEIGHT)
    surveyFolder.resizable(False, False)
    surveyFolder.focus_set()

    create_navigation_bar(surveyFolder)
    screen_width = surveyFolder.winfo_screenwidth()

    add_folder_frame = ctk.CTkFrame(surveyFolder, fg_color="#d3d3d3", height=100, corner_radius=0, width=screen_width)
    add_folder_frame.pack(fill="x", pady=10)
    add_folder_frame.pack_propagate(False)

    plus_btn = ctk.CTkButton(
        add_folder_frame, text="+", font=("Poppins", 28, "bold"),
        width=50, height=50, fg_color="white", text_color="black",
        hover_color="#bfbfbf", corner_radius=10,
        command=add_survey
    )
    plus_btn.pack(side="left", padx=20, pady=10)

    add_folder_label = ctk.CTkButton(
        add_folder_frame, text="Add new survey folder", font=("Poppins", 18, "bold"),
        fg_color="#d3d3d3", text_color="black", hover_color="#bfbfbf",
        border_width=0, corner_radius=10, command=add_survey
    )
    add_folder_label.pack(side="left", padx=10)

    surveyFolderFrame = ctk.CTkFrame(surveyFolder, fg_color="#e5e5e5")
    surveyFolderFrame.pack(fill="both", expand=True)

    canvas = tk.Canvas(surveyFolderFrame, bg="#e5e5e5", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(surveyFolderFrame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#e5e5e5")

    def update_frame_width(event):
        canvas_width = event.width
        scrollable_frame.configure(width=canvas_width)
        canvas.itemconfig(frame_window, width=canvas_width)

    canvas.bind("<Configure>", update_frame_width)
    frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Check if the user is logged in
    if is_logged_in:
        # Fetch survey folders from Firestore
        fetch_survey_folders_from_firebase()  # Fetch and display folders from Firestore
    else:
        # Load existing surveys from local directory
        load_existing_surveys()  # Load and display existing surveys

    active_windows["surveyFolder"] = surveyFolder
    close_all_windows(active_windows["surveyFolder"])

    # Bring the new window to the front
    surveyFolder.deiconify()

def add_survey():
    folder_name = custom_input_dialog()
    if folder_name:
        try:
            if is_logged_in:
                # 🔥 Check if the folder already exists in Firestore (database only)
                surveys_ref = db.collection("survey_folders") \
                    .where("folder_name", "==", folder_name) \
                    .where("user_email", "==", logged_in_email) \
                    .stream()
                existing_folders = list(surveys_ref)

                if existing_folders:
                    messagebox.showerror("Error", f"A folder with the name '{folder_name}' already exists in Firebase.")
                    return

                # If the folder does not exist in Firestore, create it in Firestore
                db.collection("survey_folders").add({
                    "user_email": logged_in_email,
                    "folder_name": folder_name,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                messagebox.showinfo("Survey", f"Folder '{folder_name}' created successfully in Firebase!", parent=surveyFolder)
                display_folder(folder_name)

            else:
                # 📁 If not logged in, create folder locally
                folder_path = os.path.join(SURVEY_DIR, folder_name)

                if os.path.exists(folder_path):
                    messagebox.showerror("Error", f"A folder with the name '{folder_name}' already exists locally.")
                    return

                os.makedirs(folder_path, exist_ok=True)
                display_folder(folder_name)  # Display the newly created folder
                messagebox.showinfo("Survey", f"Folder '{folder_name}' created successfully locally!", parent=surveyFolder)

        except Exception as e:
            messagebox.showerror("Error", f"Could not create folder:\n{str(e)}")


def delete_survey(folder_widget, folder_path, folder_name):
    try:
        if is_logged_in:
            # If logged in, delete the Firestore entry
            surveys_ref = db.collection("surveys").where("folder_name", "==", folder_name).where("user_email", "==", logged_in_email).stream()
            for survey in surveys_ref:
                # Delete the survey entry from Firestore
                db.collection("surveys").document(survey.id).delete()

            # Delete the folder from Firestore as well
            folder_ref = db.collection("survey_folders").where("folder_name", "==", folder_name).where("user_email", "==", logged_in_email).get()
            for folder in folder_ref:
                db.collection("survey_folders").document(folder.id).delete()

            # Confirm deletion
            messagebox.showinfo("Deleted", "Folder and corresponding database entries deleted successfully!")
        else:
            # If not logged in, delete the folder locally
            shutil.rmtree(folder_path)  # Recursively delete the folder and its contents
            messagebox.showinfo("Deleted", "Folder deleted successfully!")
        folder_widget.destroy()  # Remove from UI
        open_survey_folder_window()


    except Exception as e:
        messagebox.showerror("Error", f"Could not delete folder:\n{str(e)}")



        
def fetch_survey_folders_from_firebase():
    """Fetch survey folders from Firestore if the user is logged in."""
    
    if is_logged_in:
        try:
            print(f"Fetching folders for user: {logged_in_email}")  # Debugging print
            surveys_ref = db.collection("survey_folders").where("user_email", "==", logged_in_email).stream()
            survey_folders = {}

            for survey in surveys_ref:
                survey_data = survey.to_dict()
                folder_name = survey_data.get("folder_name", "Unknown")
                print(f"Found folder: {folder_name}")  # Debugging print
                if folder_name not in survey_folders:
                    survey_folders[folder_name] = []
                survey_folders[folder_name].append(survey_data)

            # Display the fetched survey folders
            for folder_name in survey_folders.keys():
                display_folder(folder_name)  # Display folder in the UI

        except Exception as e:
            print(f"Error fetching folders: {str(e)}")  # Print the error for debugging
            messagebox.showerror("Error", f"Could not fetch survey folders from Firestore:\n{str(e)}")
    else:
        # If not logged in, load local surveys
        load_existing_surveys()

def display_folder(folder_name):

    global scrollable_frame
    """Displays a folder in the survey window."""
    folder_path = os.path.join(SURVEY_DIR, folder_name)

    # Create Folder Display Frame
    folder_frame = tk.Frame(scrollable_frame, bg="#d3d3d3", padx=10, pady=5, height=200)
    folder_frame.pack(fill="x", pady=5)
    folder_frame.pack_propagate(False)

    # Load Image using Pillow
    image_path = "Folder.png"
    image_pil = Image.open(image_path).resize((150, 150), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(image_pil)

    image_label = ctk.CTkLabel(folder_frame, image=image, text="")
    image_label.image = image
    image_label.pack(side="left", padx=10)

    # Folder Info
    folder_info_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    folder_info_frame.pack(side="left", padx=10)

    folder_label = ctk.CTkLabel(folder_info_frame, text=folder_name, font=("Poppins", 16, "bold"))
    folder_label.grid(row=0, column=0, sticky="w")

    edit_label = ctk.CTkLabel(folder_info_frame, text="edit", font=("Poppins", 14, "underline"), cursor="hand2")
    edit_label.grid(row=0, column=1, sticky="w")

    # Buttons Frame
    button_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
    button_frame.pack(side="bottom", anchor="se", padx=10, pady=10)

    view_btn = ctk.CTkButton(button_frame, text="View", font=("Poppins", 14, "bold"), fg_color="#18a999", text_color="white", corner_radius=5,
                              command=lambda: view_survey_files(folder_name))  # Pass folder name to view function
    view_btn.pack(side="left", padx=5)

    delete_btn = ctk.CTkButton(button_frame, text="Delete", font=("Poppins", 14, "bold"), fg_color="#ff5252", text_color="white", corner_radius=5,
                            command=lambda: delete_survey(folder_frame, folder_path, folder_name))
    delete_btn.pack(side="left", padx=5)



def load_existing_surveys():
    folders = [f for f in os.listdir(SURVEY_DIR) if os.path.isdir(os.path.join(SURVEY_DIR, f))]
    for folder in folders:
        display_folder(folder)  # Display each folder


import pickle

def parse_survey_file(file_path):
    """Extracts Date, Location, Description, Metrics, Image Path, and Timestamp from a pickle survey file."""
    details = {
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
        with open(file_path, "rb") as file:
            survey_data = pickle.load(file)

            details["Date"] = survey_data.get("date", "Unknown")
            details["Location"] = survey_data.get("location", "Unknown")
            details["Description"] = survey_data.get("description", "No description available.")

            metrics = survey_data.get("metrics", {})
            details["Metrics"]["Horizontal Distance"] = metrics.get("Horizontal Distance", "N/A")
            details["Metrics"]["Vertical Angle"] = metrics.get("Vertical Angle", "N/A")
            details["Metrics"]["Slope"] = metrics.get("Slope", "N/A")
            details["Metrics"]["Elevation"] = metrics.get("Elevation", "N/A")

            details["Image Path"] = survey_data.get("image_path", "N/A")
            details["Timestamp"] = survey_data.get("timestamp", "N/A")

    except Exception as e:
        print(f"Error reading pickle file {file_path}: {e}")

    return details




def fetch_image_url_from_firestore(survey_id):
    """Fetch image URL of the Google Drive file from Firestore."""
    try:
        # Assuming you store the survey info in a collection 'surveys' in Firestore
        survey_ref = db.collection("surveys").document(survey_id)
        survey_doc = survey_ref.get()

        if survey_doc.exists:
            image_drive_id = survey_doc.to_dict().get("image_drive_id")
            if image_drive_id:
                # Construct the Google Drive file URL
                image_url = f"https://drive.google.com/uc?id={image_drive_id}"
                return image_url
            else:
                print("No image drive ID found in Firestore")
                return None
        else:
            print("Survey document not found")
            return None
    except Exception as e:
        print(f"Error fetching image URL from Firestore: {e}")
        return None


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


    for survey in surveys:
        file_frame = ctk.CTkFrame(scrollable_frames, fg_color="white", corner_radius=10)
        file_frame.pack(fill="x", padx=10, pady=8)

        # Top header row with title, date, and menu button
        header_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        survey_title = ctk.CTkLabel(header_frame, text="Survey", font=("Poppins", 20, "bold"))
        survey_title.pack(side="left", anchor="w")

        menu_btn = ctk.CTkButton(header_frame, text="⋮", width=30, fg_color="white", text_color="black", corner_radius=5,command=menu_button_dialog)
        menu_btn.pack(side="right")

        # Content area (address, datetime, image, and metrics)
        content_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=10, pady=10)

        # Ensure 5 columns for alignment
        for col in range(5):
            content_frame.grid_columnconfigure(col, weight=1)

        # Address (aligned with Elevation/Slope)
        address_label = ctk.CTkLabel(content_frame, text="Address", font=("Poppins", 12))
        address_label.grid(row=0, column=1, sticky="w", padx=10)

        # Corrected access to survey data
        location_label = ctk.CTkLabel(content_frame, text=survey["location"], font=("Poppins", 16, "bold", "italic"))
        location_label.grid(row=1, column=1, sticky="w", padx=10)

        # Date and Time (aligned with Elevation/Slope)
        datetime_label = ctk.CTkLabel(content_frame, text="Date and Time", font=("Poppins", 12))
        datetime_label.grid(row=0, column=3, sticky="w", padx=10)

        datetime_value = ctk.CTkLabel(content_frame, text=survey["date"], font=("Poppins", 16, "bold", "italic"))
        datetime_value.grid(row=1, column=3, sticky="w", padx=10)

        # Image
        image_label = ctk.CTkLabel(content_frame,text="")  # Label to hold the image
        image_label.grid(row=0, column=0, rowspan=4, padx=10, sticky="n")

        image_drive_id = survey.get("image_drive_id")
        if image_drive_id:
            # Construct the correct Google Drive image URL
            image_url = f"https://drive.google.com/uc?id={image_drive_id}"
            load_and_display_image(image_url, image_label)  # Pass the correct URL

          # Description
        desc_label = ctk.CTkLabel(content_frame, text="Description:", font=("Poppins", 11, "bold"))
        desc_label.grid(row=2, column=1, sticky="w", padx=(10, 2))
        desc_text = ctk.CTkLabel(content_frame, text=survey["description"], font=("Poppins", 11), anchor="w")
        desc_text.grid(row=2, column=2, columnspan=3, sticky="ew")

        # Metrics (start from row 3 to avoid clashing with address/date)
        metrics = survey.get("metrics", {})

        # Retrieve each metric with the 'get' method (this will return "N/A" if the key doesn't exist)
        metric_labels = [
            ("Elevation :", metrics.get("Elevation", "N/A")),
            ("Slope:", metrics.get("Slope", "N/A")),
            ("Horizontal Distance:", metrics.get("Horizontal Distance", "N/A")),
            ("Vertical Angle:", metrics.get("Vertical Angle", "N/A"))
        ]

        # First row of metrics (Elevation + Slope)
        elev_label = ctk.CTkLabel(content_frame, text=metric_labels[0][0], font=("Poppins", 11, "bold"))
        elev_label.grid(row=3, column=1, sticky="w", padx=10)
        elev_val = ctk.CTkLabel(content_frame, text=metric_labels[0][1], font=("Poppins", 11))
        elev_val.grid(row=3, column=2, sticky="w")

        slope_label = ctk.CTkLabel(content_frame, text=metric_labels[1][0], font=("Poppins", 11, "bold"))
        slope_label.grid(row=3, column=3, sticky="w", padx=(20, 2))
        slope_val = ctk.CTkLabel(content_frame, text=metric_labels[1][1], font=("Poppins", 11))
        slope_val.grid(row=3, column=4, sticky="w")

        # Second row of metrics (Horizontal Distance + Vertical Angle)
        hdist_label = ctk.CTkLabel(content_frame, text=metric_labels[2][0], font=("Poppins", 11, "bold"))
        hdist_label.grid(row=4, column=1, sticky="w", padx=10)
        hdist_val = ctk.CTkLabel(content_frame, text=metric_labels[2][1], font=("Poppins", 11))
        hdist_val.grid(row=4, column=2, sticky="w")

        vangle_label = ctk.CTkLabel(content_frame, text=metric_labels[3][0], font=("Poppins", 11, "bold"))
        vangle_label.grid(row=4, column=3, sticky="w", padx=(20, 2))
        vangle_val = ctk.CTkLabel(content_frame, text=metric_labels[3][1], font=("Poppins", 11))
        vangle_val.grid(row=4, column=4, sticky="w")


def view_survey_files(folder_name):
    """Displays all text files in the selected folder dynamically."""
    # Create the view window
    view_window = ctk.CTkToplevel(tk_root)
    view_window.title(f"Surveys in {folder_name}")
    view_window.geometry(f"{WIDTH}x{HEIGHT}")
    view_window.configure(bg="#e5e5e5")
    center_window(view_window, WIDTH, HEIGHT)
    view_window.resizable(False, False)

    create_navigation_bar(view_window)

    # Create a canvas and a scrollbar for scrolling
    canvas = ctk.CTkCanvas(view_window, bg="#e5e5e5", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(view_window, orientation="vertical", command=canvas.yview)

    # Create the scrollable frame inside the canvas
    scrollable_frames = ctk.CTkFrame(canvas, fg_color="#e5e5e5")

    # Function to update the frame width when the canvas is resized
    def update_frame_width(event):
        canvas_width = event.width
        scrollable_frames.configure(width=canvas_width)
        canvas.itemconfig(frame_window, width=canvas_width)

    canvas.bind("<Configure>", update_frame_width)
    
    # Create a window inside the canvas that will hold the scrollable frame
    frame_window = canvas.create_window((0, 0), window=scrollable_frames, anchor="nw")

    # Update scroll region when the content is resized
    scrollable_frames.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar into the view window
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    if is_logged_in:
        # Fetch survey details from Firestore
        try:
            surveys_ref = db.collection("surveys").where("folder_name", "==", folder_name).where("user_email", "==", logged_in_email).stream()
            surveys = []

            for survey in surveys_ref:
                survey_data = survey.to_dict()
                surveys.append(survey_data)

            # Check if any surveys were found
            if not surveys:
                messagebox.showinfo("Info", "No surveys found in this folder.")
            else:
                # Display the fetched surveys
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

            # Top header row with title, date, and menu button
            header_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))

            survey_title = ctk.CTkLabel(header_frame, text=f"Survey {index}", font=("Poppins", 20, "bold"))
            survey_title.pack(side="left", anchor="w")

            menu_btn = ctk.CTkButton(header_frame, text="⋮", width=30, fg_color="white", text_color="black", corner_radius=5,command=menu_button_dialog)
            menu_btn.pack(side="right")
            
                    # Content area (address, datetime, image, and metrics)
            content_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=10)

            # Ensure 5 columns for alignment
            for col in range(5):
                content_frame.grid_columnconfigure(col, weight=1)

            # Address (aligned with Elevation/Slope)
            address_label = ctk.CTkLabel(content_frame, text="Address", font=("Poppins", 12))
            address_label.grid(row=0, column=1, sticky="w",padx=10)

            location_label = ctk.CTkLabel(content_frame, text=survey_details["Location"],font=("Poppins", 16, "bold", "italic"))
            location_label.grid(row=1, column=1, sticky="w",padx=10)

            # Date and Time (aligned with Elevation/Slope)
            datetime_label = ctk.CTkLabel(content_frame, text="Date and Time", font=("Poppins", 12))
            datetime_label.grid(row=0, column=3, sticky="w",padx=10)

            datetime_value = ctk.CTkLabel(content_frame, text=survey_details["Date"], font=("Poppins", 16, "bold", "italic"))
            datetime_value.grid(row=1, column=3, sticky="w",padx=10)

            # Image on the left (aligned with description/metrics)
            image_path = survey_details.get("Image Path", "Folder.png")
            try:
                image_pil = Image.open(image_path).resize((250, 250), Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"Failed to load image {image_path}: {e}")
                image_pil = Image.open("Folder.png").resize((250, 250), Image.Resampling.LANCZOS)

            image = ImageTk.PhotoImage(image_pil)
            image_label = ctk.CTkLabel(content_frame, image=image, text="")
            image_label.image = image
            image_label.grid(row=0, column=0, rowspan=4, padx=10, sticky="n")
            # Description
            desc_label = ctk.CTkLabel(content_frame, text="Description:", font=("Poppins", 11, "bold"))
            desc_label.grid(row=2, column=1, sticky="w", padx=(10, 2))
            desc_text = ctk.CTkLabel(content_frame, text=survey_details["Description"], font=("Poppins", 11), anchor="w")
            desc_text.grid(row=2, column=2, columnspan=3, sticky="ew")

            # Metrics (start from row 3 to avoid clashing with address/date)
            metrics = survey_details["Metrics"]
            metric_labels = [
                ("Elevation :", metrics.get("Elevation", "N/A")),
                ("Slope:", metrics.get("Slope", "N/A")),
                ("Horizontal Distance:", metrics.get("Horizontal Distance", "N/A")),
                ("Vertical Angle:", metrics.get("Vertical Angle", "N/A"))
            ]

            # First row of metrics (Elevation + Slope)
            elev_label = ctk.CTkLabel(content_frame, text=metric_labels[0][0], font=("Poppins", 11, "bold"))
            elev_label.grid(row=3, column=1, sticky="w", padx=10)
            elev_val = ctk.CTkLabel(content_frame, text=metric_labels[0][1], font=("Poppins", 11))
            elev_val.grid(row=3, column=2, sticky="w")

            slope_label = ctk.CTkLabel(content_frame, text=metric_labels[1][0], font=("Poppins", 11, "bold"))
            slope_label.grid(row=3, column=3, sticky="w", padx=(20, 2))
            slope_val = ctk.CTkLabel(content_frame, text=metric_labels[1][1], font=("Poppins", 11))
            slope_val.grid(row=3, column=4, sticky="w")

            # Second row of metrics (Horizontal Distance + Vertical Angle)
            hdist_label = ctk.CTkLabel(content_frame, text=metric_labels[2][0], font=("Poppins", 11, "bold"))
            hdist_label.grid(row=4, column=1, sticky="w", padx=10)
            hdist_val = ctk.CTkLabel(content_frame, text=metric_labels[2][1], font=("Poppins", 11))
            hdist_val.grid(row=4, column=2, sticky="w")

            vangle_label = ctk.CTkLabel(content_frame, text=metric_labels[3][0], font=("Poppins", 11, "bold"))
            vangle_label.grid(row=4, column=3, sticky="w", padx=(20, 2))
            vangle_val = ctk.CTkLabel(content_frame, text=metric_labels[3][1], font=("Poppins", 11))
            vangle_val.grid(row=4, column=4, sticky="w")


                  


    # Store reference to the view window to prevent multiple instances
    active_windows["view_window"] = view_window

    # Close all other windows except the current one
    close_all_windows(active_windows["view_window"])
    active_windows["view_window"].deiconify()



"""END HERE"""





"""MAIN WINDOW"""
# Create main window
tk_root = ctk.CTk()
tk_root.title("EleVista")
tk_root.geometry(f"{WIDTH}x{HEIGHT}")
tk_root.iconbitmap("LOGO.ico")
tk_root.resizable(False, False)

# Center main window
center_window(tk_root, WIDTH, HEIGHT)
# tk_root.overrideredirect(True)

# Load background image
bg_image = Image.open("HomeBackground.png")
bg_image = bg_image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
bg_photo = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(WIDTH, HEIGHT))

# Create a background label
bg_label = ctk.CTkLabel(tk_root, image=bg_photo, text="", fg_color="transparent")
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ✅ Define Global is_logged_in Variable
is_logged_in = False

# ✅ Call Navigation Bar Function
create_navigation_bar(tk_root)
"""ENDS HERE"""

   
"""LOADING SCREEN"""
# Function to open loading screen
def open_loading_screen(parent_window,survey_title,description,file_path):
    # Create the loading window using customtkinter instead of tkinter
    loading_window = ctk.CTkToplevel(tk_root)
    # Add to open windows list
    open_windows.append(loading_window)
    
    loading_window.title("Loading...")
    loading_window.geometry(f"{WIDTH}x{HEIGHT}")
    loading_window.configure(fg_color="#000000")  # Black background
    
    # Center the loading window
    center_window(loading_window, WIDTH, HEIGHT)
   
    loading_window.resizable(False, False)
    loading_window.overrideredirect(True)
    
    # Disable survey window while loading is active
    parent_window.withdraw()

    # Create a container frame for the loading animation
    loading_container = ctk.CTkFrame(loading_window, width=200, height=200, fg_color="transparent")
    loading_container.place(relx=0.5, rely=0.45, anchor="center")

    # Create a canvas for the rotating arc
    canvas = tk.Canvas(loading_container, width=200, height=200, bg="black", highlightthickness=0)
    canvas.pack()

    # Initialize the loading text
    loading_texts = cycle(["loading.", "loading..", "loading..."])
    loading_text = next(loading_texts)
    
    # Function to animate the rotating arc and update the text
    angle = 0
    def animate_loading():
        nonlocal angle, loading_text
        canvas.delete("all")  # Clear the canvas
        
        # Draw the arc
        canvas.create_arc(10, 10, 190, 190, start=angle, extent=120, 
                        outline="white", width=6, style="arc")
        
        # Draw the text in the center of the canvas
        canvas.create_text(100, 100, text=loading_text, fill="white", 
                         font=("Arial", 18, "bold"))
        
        angle = (angle + 15) % 360  # Increment the angle for continuous rotation
        loading_window.after(100, animate_loading)
    
    # Function to animate the loading dots
    def animate_dots():
        nonlocal loading_text
        loading_text = next(loading_texts)
        loading_window.after(100, animate_dots)  # Update dots every 500ms

    animate_loading()
    animate_dots()

    # Status text, positioned below the loading animation
    text_label = ctk.CTkLabel(loading_window, text="EleVista is processing your image.\nPlease wait.", 
                            font=("Arial", 14, "italic"), text_color="white", fg_color="transparent")
    text_label.place(relx=0.5, rely=0.58, anchor="center")

    create_navigation_bar(loading_window) 
    # Close the loading screen after 5 seconds and show the survey result window
    def close_loading():
        if loading_window.winfo_exists():
            loading_window.destroy()
            if loading_window in open_windows:
                open_windows.remove(loading_window)
            # Open the survey result window instead of re-enabling the parent window
            surveyResult(survey_title,description,file_path)

    loading_window.after(5000, close_loading)

    # Disable main window while loading is active
    loading_window.transient(tk_root)
    loading_window.grab_set()
"""ENDS HERE"""


"""UPLOAD FILE FUNCTION"""
# Function to open survey window and display image
def upload_file():
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    
    if file_path:
        survey_window = ctk.CTkToplevel(tk_root)
        # Add to open windows list
        open_windows.append(survey_window)
        
        survey_window.title("EleVista Survey")
        survey_window.geometry(f"{WIDTH}x{HEIGHT}")   

        # Set the survey window on top and modal
        survey_window.transient(tk_root)  # Link to main window
        survey_window.grab_set()  # Make modal (disables main window)
        survey_window.focus_set()  # Focus on this window

        survey_window.configure(bg="#e5e5e5")  
        center_window(survey_window, WIDTH, HEIGHT)
        survey_window.resizable(False, False)
        # survey_window.overrideredirect(True)

        # Variables to track inputs
        title_var = tk.StringVar()
        desc_var = tk.StringVar()
        phone_var = tk.StringVar(value="Android")

        # Function to check if all fields are filled
        def validate_fields(*args):
            if title_var.get().strip() and desc_var.get().strip() and phone_var.get():
                submit_button.configure(state="normal")  # Enable button
            else:
                submit_button.configure(state="disabled")  # Disable button

        # Bind validation function to variable changes
        title_var.trace_add("write", validate_fields)
        desc_var.trace_add("write", validate_fields)
        phone_var.trace_add("write", validate_fields)

        create_navigation_bar(survey_window) 
        # Left Image Frame
        image_frame = ctk.CTkFrame(survey_window, width=500, height=500, fg_color="#ffffff")
        image_frame.pack(side="left", padx=50, pady=50)
        image_frame.pack_propagate(False)

        # Load and display image using CTkImage
        img = Image.open(file_path)
        img = img.resize((500, 500), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 500))
        img_label = ctk.CTkLabel(image_frame, image=ctk_img, text="")
        img_label.pack(expand=True, fill="both")

        # Right Form Frame
        form_frame = ctk.CTkFrame(survey_window, fg_color="transparent")
        form_frame.pack(side="right", padx=50, pady=50, fill="both", expand=True)

        survey_label = ctk.CTkLabel(form_frame, text="Survey 1", font=("Arial", 20, "bold"), text_color="#000000")
        survey_label.pack(anchor="w", pady=(0, 20))

        # Survey Title
        ctk.CTkLabel(form_frame, text="Survey Title", text_color="#000000").pack(anchor="w")
        title_entry = ctk.CTkEntry(form_frame, width=400, fg_color="#ffffff", text_color="#000000", textvariable=title_var)
        title_entry.pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(form_frame, text="Description", text_color="#000000").pack(anchor="w")
        desc_entry = ctk.CTkEntry(form_frame, width=400, fg_color="#ffffff", text_color="#000000", textvariable=desc_var)
        desc_entry.pack(pady=(0, 15))

        # Phone Selection
        ctk.CTkLabel(form_frame, text="Specify Phone Used", text_color="#000000").pack(anchor="w")
        phone_dropdown = ctk.CTkOptionMenu(
            form_frame, values=["Android", "iPhone", "Other"], width=400,
            variable=phone_var, fg_color="#ffffff", text_color="#000000"
        )
        phone_dropdown.pack(pady=(0, 20))

        # Submit Button (Initially Disabled)
        submit_button = ctk.CTkButton(
            form_frame, text="Submit", fg_color="#09AAA3", hover_color="#07A293",
            text_color="#ffffff", width=200, height=40, corner_radius=5, state="disabled",
            command=lambda: open_loading_screen(survey_window,title_entry.get(),desc_entry.get(),file_path)  # Pass survey_window to close it when loading starts
        )
        submit_button.pack(pady=20)
# Upload Button
upload_btn = ctk.CTkButton(
    tk_root, text="UPLOAD", font=("Poppins", 25, "bold"),
    fg_color="#09AAA3", text_color="white", corner_radius=5, width=200, height=50,
    command=upload_file
)
upload_btn.place(relx=0.5, rely=0.6, anchor="center")
"""ENDS HERE"""


"""SURVEY RESULT WINDOW"""

def address_dialog():
    dialog = ctk.CTkToplevel()
    dialog.title("Survey")
   
    dialog.geometry("300x175+800+300")
    dialog.configure(fg_color="white")
    dialog.resizable(False, False)
    dialog.overrideredirect(True)

    # Close Button (Top Right)
    close_button = ctk.CTkButton(
        dialog, text="✕", font=("Poppins", 14, "bold"),
        fg_color="white", text_color="#00b3b3", width=30, height=30,
        corner_radius=5, border_width=0, command=dialog.destroy
    )
    close_button.place(relx=1.0, x=-10, y=10, anchor="ne")  # Positions at the top-right

    # Label
    ctk.CTkLabel(dialog, text="Enter new address:", font=("Poppins", 14), text_color="black").pack(pady=(40, 5))

    # Entry Field
    entry = ctk.CTkEntry(dialog, font=("Poppins", 12), width=200, fg_color="white", text_color="black")
    entry.pack(pady=5)

    result = ctk.StringVar()
    def submit():
        result.set(entry.get())
        dialog.destroy()

    # OK Button (Bottom Right)
    submit_button = ctk.CTkButton(
        dialog, text="OK", command=submit, font=("Arial", 14, "bold"),
        fg_color="#00b3b3", text_color="white", corner_radius=5, width=70, height=30
    )
    submit_button.place(relx=1.0, rely=1.0, x=-15, y=-15, anchor="se")  # Bottom right positioning

    dialog.grab_set()  # Make modal
    dialog.wait_window()  # Wait until closed

    return result.get()

    

def surveyResult(survey_title,description,image):
    global image_path
    image_path = image
    if not tk_root.winfo_exists():
        print("Error: tk_root does not exist.")
        return
    
    # Create the survey detail window
    survey_result_window = ctk.CTkToplevel(tk_root)
    survey_result_window.title("EleVista - Survey Detail")
    survey_result_window.geometry(f"{WIDTH}x{HEIGHT}")
    survey_result_window.configure(bg="#e5e5e5")
    center_window(survey_result_window, WIDTH, HEIGHT)
    survey_result_window.resizable(False, False)
    survey_result_window.overrideredirect(True)
    create_navigation_bar(survey_result_window)

    # Main Content Frame
    main_frame = ctk.CTkFrame(survey_result_window, fg_color="transparent")
    main_frame.pack(pady=40, padx=20, fill="both", expand=True)  # Center the main_frame

    # Create a container frame to hold both the image and details
  # Create a container frame to hold both the image and details
    content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    content_frame.pack(expand=True)

    # Left - Image Frame
    img_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=350, height=350)
    img_frame.pack(side="left", padx=(0, 50))  # Reduced padding
    # img_frame.pack_propagate(False)  # Prevent automatic resizing

    try:
        placeholder_img = Image.open(image)
        placeholder_img = placeholder_img.resize((400, 400), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=placeholder_img, dark_image=placeholder_img, size=(400, 400))
        img_label = ctk.CTkLabel(img_frame, image=ctk_img, text="")
        img_label.pack(expand=True)
    except FileNotFoundError:
        print("Image not found. Ensure 'checkerboard.png' exists.")

       # Right - Survey Details Frame
    details_frame = ctk.CTkFrame(content_frame, fg_color="transparent", width=400)
    details_frame.pack(side="left", padx=(50, 0), fill="y", expand=False)  # Expand only as needed
    # Removed pack_propagate(False) so it resizes to fit contents

    # Title and Time
    title_label = ctk.CTkLabel(details_frame, text=survey_title, font=("Arial", 22, "bold"), text_color="#333333")
    title_label.pack(anchor="w")

    now = datetime.now()
    formatted_date_time = now.strftime("%B %d, %Y | %I:%M %p")  # Format: Month Day, Year | Hour:Minute AM/PM

    date_label = ctk.CTkLabel(details_frame, text=formatted_date_time, font=("Arial", 12, "italic"), text_color="#555555")
    date_label.pack(anchor="w")

    # Location
    location_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
    location_frame.pack(anchor="w", pady=5)

    bullet_label = ctk.CTkLabel(location_frame, text="●", font=("Arial", 12), text_color="#333333")
    bullet_label.pack(side="left")

    location_label = ctk.CTkLabel(location_frame, text="Sorosoro, Batangas City", font=("Arial", 12), text_color="#333333")
    location_label.pack(side="left", padx=5)
   
    def edit_address():
        new_address = address_dialog()
        if new_address:  # Check if the user entered a new address
            location_label.configure(text=new_address)  # Update the label with the new address

    edit_label = ctk.CTkLabel(location_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    edit_label.pack(side="left")
    edit_label.bind("<Button-1>", lambda e: edit_address())  


    # Description
    desc_label_frame = ctk.CTkFrame(details_frame, fg_color="transparent", width=350)
    desc_label_frame.pack(anchor="w", pady=3, fill="x")

    desc_label = ctk.CTkLabel(desc_label_frame, text="Description:", font=("Arial", 12, "bold"), text_color="#333333")
    desc_label.pack(side="left", pady=(10, 3))
    desc_edit_label = ctk.CTkLabel(desc_label_frame, text="edit", font=("Arial", 10, "underline"), text_color="#555555", cursor="hand2")
    desc_edit_label.pack(side="right", pady=3)

    desc_textbox = ctk.CTkTextbox(details_frame, width=350, height=100, fg_color="white", border_color="#e5e5e5", corner_radius=8)
    desc_textbox.pack(pady=5, fill="x")
    desc_textbox.insert("1.0", description)

    # Survey Metrics
    metrics = [
        ("Horizontal Distance:", "N/A"),
        ("Vertical Angle:", "N/A"),
        ("Slope:", "N/A"),
        ("Elevation:", "N/A")
    ]
    for label_text, value in metrics:
        frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        frame.pack(anchor="w", pady=2, fill="x")
        
        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 12, "bold"), text_color="#333333")
        label.pack(side="left", padx=(0, 10))  # Adds some space between label and value
        
        value_label = ctk.CTkLabel(frame, text=value, font=("Arial", 12), text_color="#333333")
        value_label.pack(side="left")

    def show_folder_selection_popup(root, folder_names):
        selected_folder = None
        popup = ctk.CTkToplevel(root)
        popup.geometry("320x180+700+450")
        popup.configure(fg_color="white")
        popup.transient(root)
        popup.grab_set()
        popup.overrideredirect(True)

        # Label
        ctk.CTkLabel(popup, text="Select a folder from your saved list:", font=ctk.CTkFont(size=14)).pack(pady=(15, 8))

        # Dropdown
        folder_var = ctk.StringVar(value=folder_names[0])
        dropdown = ctk.CTkComboBox(popup, variable=folder_var, values=folder_names, width=250)
        dropdown.pack(pady=5)

        # Internal function to handle selection
        def select_and_close():
            nonlocal selected_folder
            selected_folder = folder_var.get()
            popup.destroy()

        def cancel_and_close():
            popup.destroy()

        # Buttons
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(btn_frame, text="Select", command=select_and_close, width=90,fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=cancel_and_close, width=90,fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085").pack(side="left", padx=10)

        root.wait_window(popup)
        return selected_folder
    def choose_folder_and_save():
        if is_logged_in:
            try:
                # Fetch folders from Firestore
                folder_docs = db.collection("survey_folders").where("user_email", "==", logged_in_email).get()
                folder_names = [doc.to_dict()["folder_name"] for doc in folder_docs]

                if not folder_names:
                    messagebox.showinfo("No Folders", "No folders found in your account.", parent=popup)
                    return

                # Show folder selection popup
                selected = show_folder_selection_popup(survey_result_window, folder_names)

                # If user cancels
                if not selected:
                    return

                if selected in folder_names:
                    # 🔥 Pass just the folder name (no path) when saving to Firestore
                    save_survey_details_to_folder(selected)
                else:
                    messagebox.showwarning("Invalid", "Invalid folder name selected.", parent=popup)

            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)

        else:
            # User is not logged in — use local file dialog
            folder_selected = filedialog.askdirectory(
                parent=survey_result_window,
                initialdir=SURVEY_DIR,
                title="Select an Existing Survey Folder"
            )

            if folder_selected:
                save_survey_details_to_folder(folder_selected)
            else:
                messagebox.showwarning("Warning", "No folder selected. Please select a folder.", parent=survey_result_window)




        # Function to authenticate and get the Google Drive service
    def authenticate_google_drive():
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/drive']  # Scopes for file upload

        # Check if token.pickle exists (token for user authentication)
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials are found, prompt the user to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  # Refresh the token
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # Build the Google Drive service
        service = build('drive', 'v3', credentials=creds)
        return service

    def upload_image_to_drive(img_path, folder_id=None):
        """Upload an image to Google Drive and return the file ID."""
        # Authenticate and get the Google Drive service
        service = authenticate_google_drive()

        # Prepare the image for upload
        file_metadata = {'name': os.path.basename(img_path)}  # Use the image file name as the file name
        if folder_id:
            file_metadata['parents'] = [folder_id]  # Optionally specify a folder in Google Drive

        media = MediaFileUpload(img_path, mimetype='image/jpeg')  # You can change mimetype if the image is not jpeg

        # Upload the image to Google Drive
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

        # Make the file publicly accessible
        file_id = file['id']
        service.permissions().create(
            fileId=file_id,
            body={
                'role': 'reader',  # Give read permissions
                'type': 'anyone'   # Allow anyone to access it
            }
        ).execute()

        print(f"File uploaded successfully. File ID: {file_id}")
        # Return the file ID and the public link
        global public_link
        public_link = f"https://drive.google.com/uc?id={file_id}"
        print(f"Public Link: {public_link}")
        return file_id

    def save_to_new_survey_folder():
        # Ask user to name the new survey folder
        folder_name = custom_input_dialog()

        if not folder_name:
            messagebox.showwarning("Cancelled", "Folder creation cancelled.", parent=survey_result_window)
            return

        # Get values from UI
        date = date_label.cget("text").strip()
        location = location_label.cget("text").strip()
        description = desc_textbox.get("1.0", tk.END).strip()

        if not date or not location or not description:
            messagebox.showwarning("Warning", "Please ensure all fields are filled before saving.", parent=survey_result_window)
            return

        # Survey Metrics (static for now)
        metrics = {
            "Horizontal Distance": "N/A",
            "Vertical Angle": "N/A",
            "Slope": "N/A",
            "Elevation": "N/A"
        }

        try:
            if is_logged_in:
                # 🖼️ Prompt user to select an image file (optional)
                image_url = None
                if image_path:
                    # Upload image to Google Drive and get the file ID
                    file_id = upload_image_to_drive(image_path)  # Upload to Google Drive

                    if not file_id:
                        messagebox.showwarning("Error", "Failed to upload image to Google Drive.", parent=survey_result_window)
                        return

                    # Construct the public URL for the uploaded image (optional)
                    # image_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

                # 🔒 Save to Firestore
                db.collection("survey_folders").add({
                    "user_email": logged_in_email,
                    "folder_name": folder_name,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })

                db.collection("surveys").add({
                    "user_email": logged_in_email,
                    "folder_name": folder_name,
                    "date": date,
                    "location": location,
                    "description": description,
                    "metrics": metrics,
                    "image_drive_id": file_id,  # 🔗 Link to image uploaded on Google Drive
                    "timestamp": firestore.SERVER_TIMESTAMP
                })

                messagebox.showinfo("Success", f"Survey details saved to the database under folder:\n{folder_name}.")

            else:
                # 📁 Save to local directory only (If not logged in)
                new_folder_path = os.path.join(SURVEY_DIR, folder_name)

                if os.path.exists(new_folder_path):
                    messagebox.showerror("Error", "A folder with this name already exists.", parent=survey_result_window)
                    return

                os.makedirs(new_folder_path)

                # 🖼️ If image exists, copy it locally
                image_path_local = None
                if image_path:
                    local_image_path = os.path.join(new_folder_path, os.path.basename(image_path))

                    try:
                        shutil.copy(image_path, local_image_path)
                        image_path_local = local_image_path  # Store the local image path
                        print(f"Image saved locally at: {local_image_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not save image locally: {str(e)}", parent=survey_result_window)
                        return

                # Create survey metadata dictionary
                survey_metadata = {
                    "folder_name": folder_name,
                    "date": date,
                    "location": location,
                    "description": description,
                    "metrics": metrics,
                    "image_path": image_path_local,  # Store the local image path
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pickle_file_name = f"survey_data_{timestamp}.pkl"  # Use a fixed name for the file
                pickle_file_path = os.path.join(new_folder_path, pickle_file_name)  # Join with the folder path
                with open(pickle_file_path, 'wb') as pickle_file:
                    pickle.dump(survey_metadata, pickle_file)

                messagebox.showinfo("Success", f"Survey details saved locally in:\n{pickle_file_path}.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save survey:\n{str(e)}", parent=survey_result_window)




    def save_survey_details_to_folder(folder_selected):
        # Get values from the UI fields
        date = date_label.cget("text").strip()
        location = location_label.cget("text").strip()
        description = desc_textbox.get("1.0", tk.END).strip()

        # Survey Metrics (static for now)
        metrics = {
            "Horizontal Distance": "N/A",
            "Vertical Angle": "N/A",
            "Slope": "N/A",
            "Elevation": "N/A"
        }

        # Ensure required fields are not empty
        if not date or not location or not description:
            messagebox.showwarning("Warning", "Please ensure all fields are filled before saving.", parent=survey_result_window)
            return

        try:
            if is_logged_in:
                # 🔒 Save to Firestore only
                image_url = None
                image_drive_id = None
                if image_path:
                    # Upload image to Google Drive and get the file ID
                    image_drive_id = upload_image_to_drive(image_path)

                    if not image_drive_id:
                        messagebox.showwarning("Error", "Failed to upload image to Google Drive.", parent=survey_result_window)
                        return

                folder_name = os.path.basename(folder_selected)  # This is just the name, not a path

                # Check if folder exists in Firestore
                folder_query = db.collection("survey_folders") \
                    .where("user_email", "==", logged_in_email) \
                    .where("folder_name", "==", folder_name).get()

                if not folder_query:
                    db.collection("survey_folders").add({
                        "user_email": logged_in_email,
                        "folder_name": folder_name,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })

                # Save the survey details to Firestore
                db.collection("surveys").add({
                    "user_email": logged_in_email,
                    "folder_name": folder_name,
                    "date": date,
                    "location": location,
                    "description": description,
                    "metrics": metrics,
                    "image_drive_id": image_drive_id,  # Store the Google Drive file ID
                    "timestamp": firestore.SERVER_TIMESTAMP
                })

                messagebox.showinfo("Success", "Survey details saved to the database.")

            else:
                # 📁 Save locally only
                # Ensure the local folder exists
                if not os.path.exists(folder_selected):
                    os.makedirs(folder_selected)
                    print(f"Created folder: {folder_selected}")

                # If image exists, copy it locally
                image_path_local = None
                if image_path:
                    local_image_path = os.path.join(folder_selected, os.path.basename(image_path))

                    try:
                        shutil.copy(image_path, local_image_path)
                        image_path_local = local_image_path  # Store the local image path
                        print(f"Image saved locally at: {local_image_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not save image locally: {str(e)}", parent=survey_result_window)
                        return

                # Create survey metadata dictionary
                survey_metadata = {
                    "folder_name": folder_selected,
                    "date": date,
                    "location": location,
                    "description": description,
                    "metrics": metrics,
                    "image_path": image_path_local,  # Store the local image path
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pickle_file_name = f"survey_data_{timestamp}.pkl"  # Use a fixed name for the file
                pickle_file_path = os.path.join(folder_selected, pickle_file_name)  # Join with the folder path

                print(f"Saving survey metadata to: {pickle_file_path}")
                with open(pickle_file_path, 'wb') as pickle_file:
                    pickle.dump(survey_metadata, pickle_file)

                messagebox.showinfo("Success", f"Survey details saved locally in:\n{pickle_file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save survey:\n{str(e)}", parent=survey_result_window)



    def popup_save():
        popup = ctk.CTkToplevel(tk_root)
        popup.geometry("200x125+800+500")
        popup.configure(fg_color="white")
        popup.overrideredirect(True)

        # Close Button (Top Right)
        close_button = ctk.CTkButton(
            popup, text="X", font=("Poppins", 14, "bold"),
            fg_color="white", text_color="#00b3b3", width=30, height=30,
            corner_radius=0, border_width=0, command=popup.destroy
        )
        close_button.place(relx=1.0, x=-5, y=5, anchor="ne")  # Positions at the top-right

        def save_new_and_close():
            popup.destroy()
            save_to_new_survey_folder()

        new_button = ctk.CTkButton(
        popup, text="Save to New Folder", fg_color="white", text_color="black",
        hover_color="#1abc9c", command=save_new_and_close
    )
        new_button.pack(pady=(40, 5))

        # Existing Button
        existing_button = ctk.CTkButton(
            popup, text="Save to Existing Folder", fg_color="white", text_color="black",
            hover_color="#1abc9c", command=choose_folder_and_save
        )
        existing_button.pack(pady=5)

    # Create a bottom frame for the button
    button_frame = ctk.CTkFrame(survey_result_window, fg_color="transparent")
    button_frame.pack(side="bottom", fill="x", pady=20, padx=20, anchor="se")

    # Save button
    save_button = ctk.CTkButton(button_frame, text="SAVE", fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085",command=popup_save)
    save_button.pack(side="right", padx=10)


    def delTemp():
        messagebox.showinfo("Deleted","You have deleted!")
        go_home()

    delete_button = ctk.CTkButton(button_frame, text="DELETE", fg_color="#1abc9c", 
                                text_color="white", hover_color="#16a085",command=delTemp)
    delete_button.pack(side="right", padx=20)
"""ENDS HERE"""
   


# Run Application
tk_root.mainloop()








