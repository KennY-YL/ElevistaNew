import customtkinter as ctk
from constants import WIDTH, HEIGHT
from firebase_service import firebase_service
from auth import auth_manager
from nav_bar import NavigationBar  
from utils.utils import center_window
# Import your page functions
from pages.home import show_home
from pages.about_us import show_about_us
from pages.manual import open_instruction_window
from pages.survey import open_survey_folder_window
from pages.upload import upload_file  # if you have an upload page
from pages.login import show_login_window

def run_app():
    """Launch the main application."""
    global root, navbar, content_container
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("EleVista Survey App")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)
    center_window(root, WIDTH, HEIGHT)
    # Initialize Firebase
    firebase_service.initialize()

    # Load remember me credentials
    email, password = auth_manager.load_credentials()

    # Setup Navigation Bar
    navbar = NavigationBar(root, auth_manager, app_navigator)  # ✅ Correct way

   
    content_container = ctk.CTkFrame(root, fg_color="#f5f5f5")
    content_container.pack(fill="both", expand=True)


    firebase_service.test_connection()
    # Default page
    show_home(content_container)


    root.mainloop()

def app_navigator(destination):
    if destination == "home":
        navigate_to_home()
    elif destination == "about_us":
        navigate_to_about_us()
    elif destination == "manual":
        navigate_to_manual()
    elif destination == "surveys":
        navigate_to_survey()
    elif destination == "upload":
        navigate_to_upload()
    elif destination == "login":
        login_overlay = navigate_to_login(close_overlay=lambda: close_login(login_overlay))  # Capture login_overlay here
    elif destination == "signup":
        pass  # Handle signup navigation


# Navigation Handlers
def navigate_to_home():
    show_home(content_container)

def navigate_to_about_us():
    show_about_us(content_container)

def navigate_to_manual():
    open_instruction_window(content_container)

def navigate_to_survey():
    open_survey_folder_window(content_container)

def navigate_to_upload():
    upload_file(content_container)


def navigate_to_login(close_overlay=None):
    # Create login overlay frame
    login_overlay = ctk.CTkFrame(root, fg_color="white")
    login_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)  # Fullscreen overlay

    # Show the login UI inside the overlay
    show_login_window(login_overlay, close_overlay=close_overlay)

    # Optionally hide navbar and content temporarily
    if hasattr(navbar, 'hide'):  # Check if navbar has a custom hide method
        navbar.hide()
    else:
        # Use pack_forget() if navbar is a CTkFrame
        try:
            navbar.pack_forget()
        except AttributeError:
            print("Navbar doesn't have pack_forget() method!")

    content_container.pack_forget()  # Hide content container temporarily

    return login_overlay  # Return login_overlay for later use

def close_login(login_overlay):
    # Destroy the login overlay and navigate back to the home page
    login_overlay.destroy()

    # Show the navbar again if you used pack_forget()
    if hasattr(navbar, 'show'):  # If navbar has a custom show method
        navbar.show()
    else:
        # If navbar is a CTkFrame, use pack() again to restore it
        try:
            navbar.pack(fill="both", expand=True)  # Adjust as needed
        except AttributeError:
            print("Navbar doesn't have pack method!")

    # Restore the content container
    content_container.pack(fill="both", expand=True)  # Show the content container again

    # Go back to the home page
    app_navigator("home")  # Go back to the home page
