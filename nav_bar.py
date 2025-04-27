# nav_bar.py

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from constants import LOGO_IMAGE, PROFILE_IMAGE, LOGOUT_IMAGE
from utils.utils import clear_content
from pages.home import show_home
from pages.survey import open_survey_folder_window
from pages.manual import open_instruction_window
from pages.about_us import show_about_us

class NavigationBar:
    def __init__(self, parent, auth_manager, app_navigator):
        self.parent = parent
        self.auth_manager = auth_manager
        self.app_navigator = app_navigator

        self.header_frame = None
        self.nav_frame = None
        self.profile_section = None
        self.profile_image = None
        self.logout_image = None

        self.build_navbar()

    def build_navbar(self):
        # Destroy old header frame
        if self.header_frame and self.header_frame.winfo_exists():
            self.header_frame.destroy()

        # Header
        self.header_frame = tk.Frame(self.parent, height=70, bg="#0f0f0f")
        self.header_frame.pack(side="top", fill="x", pady=0)

        # Logo
        logo_img = Image.open(LOGO_IMAGE).resize((50, 50), Image.Resampling.LANCZOS)
        logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(50, 50))

        logo_label = ctk.CTkLabel(self.header_frame, image=logo_ctk, text="", fg_color="transparent")
        logo_label.pack(side="left", padx=(30, 10))

        title_label = ctk.CTkLabel(self.header_frame, text="EleVista", font=("Poppins", 30), text_color="white", fg_color="transparent")
        title_label.pack(side="left", padx=(0, 30))

        # Destroy old nav frame
        if self.nav_frame and self.nav_frame.winfo_exists():
            self.nav_frame.destroy()

        self.nav_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.nav_frame.pack(side="right", padx=20, pady=15)

        self.add_nav_buttons()

    def add_nav_buttons(self):
        # Navigation buttons always available
        buttons = [
            ("Home", lambda: self.app_navigator("home")),
            ("Surveys", lambda: self.app_navigator("surveys")),
            ("Manual", lambda: self.app_navigator("manual")),
            ("About Us", lambda: self.app_navigator("about_us")),
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                self.nav_frame, text=text, font=("Poppins", 20),
                fg_color="transparent", text_color="white",
                hover_color="#09AAA3", corner_radius=5,
                width=120, height=40, command=command
            )
            btn.pack(side="left", padx=10)

        # If user is logged in
        if self.auth_manager.is_logged_in:
            self.add_profile_section()
        else:
            self.add_auth_buttons()

    def add_auth_buttons(self):
        login_btn = ctk.CTkButton(
            self.nav_frame, text="LOGIN", font=("Poppins", 20),
            fg_color="#09AAA3", text_color="white",
            corner_radius=5, width=120, height=40,
            command=lambda: self.app_navigator("login")
        )
        login_btn.pack(side="left", padx=10)

        signup_btn = ctk.CTkButton(
            self.nav_frame, text="SIGN UP", font=("Poppins", 20),
            fg_color="transparent", text_color="white",
            border_color="#09AAA3", border_width=2,
            corner_radius=5, width=120, height=40,
            hover_color="#09AAA3",
            command=lambda: self.app_navigator("signup")
        )
        signup_btn.pack(side="left", padx=10)

    def add_profile_section(self):
        # Profile section with profile pic, email, and logout button
        self.profile_section = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        self.profile_section.pack(side="left", padx=10)

        profile_img = Image.open(PROFILE_IMAGE).resize((30, 30), Image.Resampling.LANCZOS)
        self.profile_image = ctk.CTkImage(light_image=profile_img, dark_image=profile_img, size=(30, 30))

        profile_btn = ctk.CTkButton(
            self.profile_section, text="", image=self.profile_image,
            width=40, height=40,
            fg_color="transparent", hover_color="#09AAA3",
            command=self.logout_popup
        )
        profile_btn.pack(side="left", padx=(0, 5))

        name_label = ctk.CTkLabel(
            self.profile_section,
            text=self.auth_manager.logged_in_email,
            font=("Poppins", 14), text_color="white", fg_color="transparent"
        )
        name_label.pack(side="left", padx=(0, 10))

        # Logout icon button
        logout_img = Image.open(LOGOUT_IMAGE).resize((20, 20), Image.Resampling.LANCZOS)
        self.logout_image = ctk.CTkImage(light_image=logout_img, dark_image=logout_img, size=(20, 20))

        logout_btn = ctk.CTkButton(
            self.profile_section, text="", image=self.logout_image,
            fg_color="transparent", hover_color="#09AAA3",
            width=40, height=40,
            command=self.logout_popup
        )
        logout_btn.pack(side="left")

    def logout_popup(self):
        result = messagebox.askyesno("Logout", "Do you really want to logout?")
        if result:
            self.auth_manager.logout()
            self.build_navbar()   # Refresh nav bar
            self.app_navigator("home")   # Go to home

