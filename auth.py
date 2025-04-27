# auth.py

import json
import os
from tkinter import messagebox
from constants import REMEMBER_ME_FILE
from firebase_service import FirebaseService

class AuthManager:
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service
        self.logged_in_email = None
        self.is_logged_in = False

    def save_credentials(self, email, password):
        """Save credentials locally (Remember Me)."""
        try:
            with open(REMEMBER_ME_FILE, "w") as f:
                json.dump({"email": email, "password": password}, f)
            print(" Credentials saved.")
        except Exception as e:
            print(f"Error saving credentials: {str(e)}")

    def load_credentials(self):
        """Load saved credentials."""
        if os.path.exists(REMEMBER_ME_FILE):
            try:
                with open(REMEMBER_ME_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("email", ""), data.get("password", "")
            except Exception as e:
                print(f"Error loading credentials: {str(e)}")
        return "", ""

    def login(self, email, password, remember=False):
        """Login user by verifying email and password."""
        users = self.firebase_service.get_user_by_email(email)

        for user in users:
            if user["password"] == password:
                self.is_logged_in = True
                self.logged_in_email = email

                if remember:
                    self.save_credentials(email, password)

                print(f" {email} logged in successfully.")
                return True

        print(" Invalid email or password.")
        return False


    def logout(self):
        """Logout user and clear state."""
        self.is_logged_in = False
        self.logged_in_email = None
        print(" Logged out successfully.")

    def signup(self, email, password, confirm_password):
        """Sign up a new user."""
        if not email or not password or not confirm_password:
            raise ValueError("Please fill all fields.")

        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        try:
            self.firebase_service.create_user(email, password)
            print(f"Account created for {email}.")
            return True
        except Exception as e:
            print(f" Error during signup: {str(e)}")
            return False
# Create a global AuthManager instance
from firebase_service import firebase_service
auth_manager = AuthManager(firebase_service)