import customtkinter as ctk
import tkinter as tk
from auth import auth_manager
from utils.utils import toggle_password, clear_content
from firebase_service import firebase_service
from PIL import Image
from constants import LOGIN_BACKGROUND, HEIGHT, WIDTH, HIDE_IMAGE
from pages.home import show_home



def show_login_window(content_container, on_login_success=None, close_overlay=None):
    clear_content(content_container)

    # Create login frame
    login_frame = ctk.CTkFrame(content_container, fg_color="transparent")
    login_frame.pack(fill="both", expand=True)

    # Load and display background image
    bg_image = ctk.CTkImage(Image.open(LOGIN_BACKGROUND), size=(WIDTH, HEIGHT))
    bg_label = ctk.CTkLabel(login_frame, image=bg_image, text="")
    bg_label.pack(fill="both", expand=True)  # Use pack for background so it stretches properly

    # Create the form frame on top of background
    form_frame = ctk.CTkFrame(login_frame, fg_color="#FFFFFF", corner_radius=5, width=450, height=500)
    form_frame.place(relx=0.5, rely=0.55, anchor="center")
    form_frame.pack_propagate(False)  # Prevent it from shrinking to its children's size

    # Load saved credentials
    saved_email, saved_password = auth_manager.load_credentials()

    close_button = ctk.CTkButton(
        login_frame,
        text="X",
        font=("Poppins", 20),  # same font size as your nav buttons
        fg_color="black",
        text_color="white",
        hover_color="#09AAA3",
        corner_radius=0,
        width=40,
        height=40,
        command=close_overlay  # Call the close_overlay function when close button is clicked
    )
    close_button.place(x=1150, y=20)  # Position close button

    # Title
    ctk.CTkLabel(form_frame, text="LOGIN", font=("Poppins", 30, "bold"), text_color="#09AAA3").pack(pady=(50, 20))

    # Email
    ctk.CTkLabel(form_frame, text="Email", font=("Poppins", 14)).pack(anchor="w", padx=50)
    email_entry = ctk.CTkEntry(form_frame, width=350, font=("Poppins", 14))
    email_entry.insert(0, saved_email)
    email_entry.pack(anchor="w", pady=10, padx=52)

    # Password
    ctk.CTkLabel(form_frame, text="Password", font=("Poppins", 14)).pack(anchor="w", padx=50, pady=(10, 0))
    password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    password_frame.pack(pady=5)

    # Password Entry
    password_entry = ctk.CTkEntry(password_frame, width=350, font=("Poppins", 14), show="*")
    password_entry.pack(side="left", padx=(35, 0))
    password_entry.insert(0, saved_password)

    # Load the hide icon properly
    hide_icon = ctk.CTkImage(light_image=Image.open(HIDE_IMAGE), dark_image=Image.open(HIDE_IMAGE))

    # Toggle button for password visibility
    toggle_button = ctk.CTkButton(
        password_frame, text="", width=30, height=30, fg_color="transparent",
        image=hide_icon, command=lambda: toggle_password(password_entry, toggle_button)
    )
    toggle_button.pack(side="left")

    # Remember Me
    remember_var = tk.BooleanVar(value=bool(saved_email))
    ctk.CTkCheckBox(form_frame, text="Remember Me ?", variable=remember_var, font=("Poppins", 12)).pack(anchor="w", padx=50, pady=10)

    # Login handler
    def handle_login():
        success = auth_manager.login(email_entry.get(), password_entry.get(), remember_var)
        if success:
            auth_manager.is_logged_in = True   # Set logged-in status
            if close_overlay:
                close_overlay()   # Destroy the login overlay frame
            show_home(content_container)  # Show the home page directly here
            print("Login successful!")
                

    # Login button
    ctk.CTkButton(
        form_frame, text="LOGIN", font=("Poppins", 14, "bold"),
        fg_color="#00b3b3", text_color="white", width=200, height=40,
        command=handle_login
    ).pack(pady=20)

    # Forgot password
    ctk.CTkLabel(
        form_frame, text="Forgot Password ?", text_color="gray",
        fg_color="transparent", font=("Poppins", 12), cursor="hand2"
    ).pack()

    # Divider
    ctk.CTkLabel(
        form_frame, text="_________________ or _________________",
        text_color="gray", fg_color="transparent", font=("Poppins", 12)
    ).pack(pady=7)

    # Signup
    signup_label = ctk.CTkLabel(
        form_frame, text="Need an account? SIGN UP", text_color="#00b3b3",
        font=("Poppins", 12, "bold"), cursor="hand2"
    )
    signup_label.pack(pady=5)


    # signup_label.bind("<Button-1>", lambda e: show_signup_window())  # Uncomment if you have a signup window
