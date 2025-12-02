import uuid
from seleniumbase import BaseCase
import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

class TestEndToEndAuth(BaseCase):

    def generate_credentials(self):
        username = "user_" + uuid.uuid4().hex[:6]
        email = f"{username}@test.com"
        password = "Password123!"
        return username, email, password

    def wait_for_url_contains(self, substring, timeout=10):
        """Helper function to wait until current URL contains substring"""
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if substring in self.get_current_url():
                return True
            self.sleep(0.5)
        raise Exception(f"URL did not contain '{substring}' after {timeout} seconds.")

    def test_register_login_profile_logout(self):
        username, email, password = self.generate_credentials()
        new_pw = "NewPassword456!"

        # ------------------
        # Register
        # ------------------
        self.open(f"{BASE_URL}/register")
        self.wait_for_element("#username")
        self.type("#username", username)
        self.type("#email", email)
        self.type("#password", password)
        self.type("#confirmPassword", password)
        self.click("button[type='submit']")
        self.wait_for_element("#registerMessage")
        self.assert_text("Redirecting", "#registerMessage")

        # ------------------
        # Login
        # ------------------
        self.open(f"{BASE_URL}/login")
        self.wait_for_element("#username")
        self.type("#username", username)
        self.type("#password", password)
        self.click("button[type='submit']")
        
        # Wait until the URL contains /dashboard
        self.wait_for_url_contains("/dashboard", timeout=15)

        # ------------------
        # Profile Page
        # ------------------
        self.open(f"{BASE_URL}/profile")
        self.wait_for_element("#profileCard")
        self.assert_element("#username")
        self.assert_element("#email")

        # ------------------
        # Change Password
        # ------------------
        self.wait_for_element("#oldPassword")
        self.type("#oldPassword", password)
        self.type("#newPassword", new_pw)
        self.type("#confirmNewPassword", new_pw)
        self.click("button[type='submit']")
        self.wait_for_element("#changePasswordMessage")
        self.assert_text("success", "#changePasswordMessage")

        # ------------------
        # Logout
        # ------------------
        self.wait_for_element("#navbarDropdown")
        self.click("#navbarDropdown")
        self.wait_for_element("#logoutBtn")
        self.click("#logoutBtn")
        self.wait_for_url_contains("/login", timeout=10)
