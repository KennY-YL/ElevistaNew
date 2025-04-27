import os
import customtkinter as ctk
from constants import VIEW_IMAGE, HIDE_IMAGE
from customtkinter import CTkImage
from PIL import Image 
def clear_content(container):
    """Remove all widgets from a given container."""
    for widget in container.winfo_children():
        widget.destroy()

def center_window(window, width, height):
    """Center a window on the screen."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update()

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



def toggle_password(password_entry,toggle_button):
    """Toggle password visibility and switch eye icon."""
    eye_open_img = ctk.CTkImage(Image.open(VIEW_IMAGE), size=(20, 20))
    eye_closed_img = ctk.CTkImage(Image.open(HIDE_IMAGE), size=(20, 20))
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")  # Show password
        toggle_button.configure(image=eye_open_img)  # Switch to open eye image
    else:
        password_entry.configure(show="*")  # Hide password
        toggle_button.configure(image=eye_closed_img)  # Switch to closed eye image

# def menu_button_dialog():


#     if menu_dialog and menu_dialog.winfo_exists():
#         menu_dialog.destroy()
#         menu_dialog = None
#     else:
#         menu_dialog = ctk.CTkToplevel(tk_root)
#         menu_dialog.geometry("220x120+1500+169")
#         menu_dialog.configure(fg_color="white")
#         menu_dialog.overrideredirect(True)

#         # Download Button
#         download_button = ctk.CTkButton(menu_dialog, text="Download", fg_color="black", text_color="white",
#                                       hover_color="gray")
#         download_button .pack(pady=10)


#         # Delete Button
#         delete_button = ctk.CTkButton(menu_dialog, text="Delete", fg_color="black", text_color="white",
#                                       hover_color="gray")
#         delete_button.pack(pady=10)