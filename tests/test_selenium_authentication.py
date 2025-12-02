import uuid
from seleniumbase import BaseCase

BASE_URL = "http://localhost:5000"


class TestEndToEndAuth(BaseCase):

    def test_register_login_profile_logout(self):
        # Generate unique credentials
        username = "user_" + uuid.uuid4().hex[:6]
        email = f"{username}@test.com"
        password = "Password123!"

        # ------------------
        # Register
        # ------------------
        self.open(f"{BASE_URL}/register")

        self.type("#username", username)
        self.type("#email", email)
        self.type("#password", password)
        self.type("#confirmPassword", password)

        self.click("button[type='submit']")

        self.assert_text("Redirecting", "#registerMessage")

        # ------------------
        # Login
        # ------------------
        self.open(f"{BASE_URL}/login")

        self.type("#username", username)
        self.type("#password", password)
        self.click("button[type='submit']")

        self.wait_for_url_contains("/dashboard")

        # ------------------
        # Profile Page
        # ------------------
        self.open(f"{BASE_URL}/profile")

        self.assert_element("#profileCard")
        self.assert_element("#username")
        self.assert_element("#email")

        # ------------------
        # Change Password
        # ------------------
        new_pw = "NewPassword456!"

        self.type("#oldPassword", password)
        self.type("#newPassword", new_pw)
        self.type("#confirmNewPassword", new_pw)
        self.click("button[type='submit']")

        self.assert_text_contains("success", "#changePasswordMessage")

        # ------------------
        # Logout
        # ------------------
        self.click("#navbarDropdown")
        self.click("#logoutBtn")

        self.wait_for_url_contains("/login")


    def test_reset_page_validation(self):
        self.open(f"{BASE_URL}/auth/reset-password")

        self.type("#newPassword", "abc123")
        self.type("#confirmPassword", "wrong")
        self.click("button[type='submit']")

        self.assert_text_contains("match", "#resetMessage")
