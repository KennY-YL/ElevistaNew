import tkinter as tk
from tkinter import messagebox

def login():
    username = email_entry.get()
    password = password_entry.get()
    
    if username == "admin" and password == "password":  # Sample credentials
        messagebox.showinfo("Login Successful", "Welcome!")
        login_window.destroy()
    else:
        messagebox.showerror("Login Failed", "Invalid email or password.")

def close_window():
    login_window.destroy()

def show_login_window():
    global login_window, email_entry, password_entry, remember_var

    login_window = tk.Toplevel()
    login_window.title("Login")
    login_window.geometry("400x400")
    login_window.configure(bg="#F7F7F7")  # Light background

    # Close Button (X)
    close_button = tk.Button(
        login_window, text="X", font=("Arial", 12, "bold"),
        fg="cyan", bg="#F7F7F7", bd=0, command=close_window
    )
    close_button.place(x=370, y=10)

    # Login Label
    login_label = tk.Label(
        login_window, text="LOGIN", font=("Arial", 14, "bold"),
        fg="cyan", bg="#F7F7F7"
    )
    login_label.pack(pady=(20, 5))

    # Email Label & Entry
    tk.Label(login_window, text="Email", bg="#F7F7F7").pack(anchor="w", padx=50)
    email_entry = tk.Entry(login_window, width=30, font=("Arial", 12))
    email_entry.pack(pady=5)

    # Password Label & Entry
    tk.Label(login_window, text="Password", bg="#F7F7F7").pack(anchor="w", padx=50)
    password_entry = tk.Entry(login_window, width=30, font=("Arial", 12), show="*")
    password_entry.pack(pady=5)

    # Remember Me Checkbox
    remember_var = tk.BooleanVar()
    remember_me = tk.Checkbutton(
        login_window, text="Remember Me ?", variable=remember_var,
        bg="#F7F7F7"
    )
    remember_me.pack(anchor="w", padx=50, pady=5)

    # Login Button
    login_btn = tk.Button(
        login_window, text="LOGIN", font=("Arial", 12, "bold"),
        fg="white", bg="cyan", width=20, height=1,
        command=login
    )
    login_btn.pack(pady=10)

    # Forgot Password Label
    forgot_label = tk.Label(
        login_window, text="Forgot Password ?", fg="gray",
        bg="#F7F7F7", cursor="hand2"
    )
    forgot_label.pack()

    # Divider Line
    tk.Label(login_window, text="________________ or ________________", fg="gray", bg="#F7F7F7").pack(pady=5)

    # Signup Link
    signup_label = tk.Label(
        login_window, text="Need an account? SIGNUP", fg="cyan",
        bg="#F7F7F7", font=("Arial", 10, "bold"), cursor="hand2"
    )
    signup_label.pack(pady=5)

    login_window.mainloop()

# Main Tkinter window
root = tk.Tk()
root.withdraw()  # Hide the main window
