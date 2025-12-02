import uuid
from seleniumbase import BaseCase
import os

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


class TestFitnessApp(BaseCase):
    """
    End-to-end Selenium tests for Fitness Tracker app functionality:
    - Dashboard links verification
    - Recipe creation and saving
    - Workout creation and saving
    - Statistics charts display
    """

    # -------------------------
    # Helper Functions
    # -------------------------
    def generate_credentials(self):
        """
        Generate a unique username, email, and password for registration.
        Returns: (username, email, password)
        """
        username = "user_" + uuid.uuid4().hex[:6]
        email = f"{username}@test.com"
        password = "Password123!"
        return username, email, password

    def wait_for_url_contains(self, substring, timeout=10):
        """
        Wait until the current URL contains the specified substring.
        Raises an Exception if the timeout is reached.
        """
        import time
        end_time = time.time() + timeout
        while time.time() < end_time:
            if substring in self.get_current_url():
                return True
            self.sleep(0.5)
        raise Exception(f"URL did not contain '{substring}' after {timeout} seconds.")

    def register_and_login(self):
        """
        Helper function to register a new user and log in.
        Returns: (username, password)
        """
        username, email, password = self.generate_credentials()

        # -------------------------
        # Register
        # -------------------------
        self.open(f"{BASE_URL}/register")
        self.wait_for_element("#username")
        self.type("#username", username)
        self.type("#email", email)
        self.type("#password", password)
        self.type("#confirmPassword", password)
        self.click("button[type='submit']")
        self.wait_for_element("#registerMessage")
        self.assert_text("Redirecting", "#registerMessage")

        # -------------------------
        # Login
        # -------------------------
        self.open(f"{BASE_URL}/login")
        self.wait_for_element("#username")
        self.type("#username", username)
        self.type("#password", password)
        self.click("button[type='submit']")
        self.wait_for_url_contains("/dashboard", timeout=15)
        return username, password

    # -------------------------
    # Dashboard Tests
    # -------------------------
    def test_dashboard_links(self):
        """
        Verify that all expected dashboard links and profile elements are present.
        """
        self.register_and_login()

        # Verify top dashboard links
        self.assert_element("a[href='/workouts/ui']")
        self.assert_element("a[href='/workouts/ui/create']")
        self.assert_element("a[href='/recipes/ui']")
        self.assert_element("a[href='/recipes/ui/create']")
        self.assert_element("a[href='/stats/ui']")

        # Scroll to and verify profile card
        profile_btn = "div.bg-body-tertiary a[href='/profile']"
        self.scroll_to(profile_btn)
        self.wait_for_element_visible(profile_btn, timeout=15)
        self.assert_element(profile_btn)

    # -------------------------
    # Recipe Tests
    # -------------------------
    def test_create_and_save_recipe(self):
        """
        Test creating a recipe using external API search and saving it to cookbook.
        """
        self.register_and_login()
        self.open(f"{BASE_URL}/recipes/ui/create")

        # Search for meal
        self.wait_for_element("#mealInput")
        self.type("#mealInput", "Chicken")
        self.execute_script("document.querySelector('#search-pane button.btn-primary').click()")
        self.wait_for_element("#mealResults .card", timeout=15)

        # Save first recipe from search results
        first_save_btn = self.find_elements("#mealResults button.btn-outline-success")[0]
        self.execute_script("arguments[0].click();", first_save_btn)
        self.accept_alert()  # confirm save
        self.accept_alert()  # confirm success

        # Verify redirect to cookbook
        self.wait_for_url_contains("/recipes/ui", timeout=15)
        self.assert_text("My Cookbook", "h2")

    # -------------------------
    # Workout Tests
    # -------------------------
    def test_add_and_save_workout(self):
        """
        Test creating a workout session and saving it.
        """
        self.register_and_login()
        self.open(f"{BASE_URL}/workouts/ui/create")

        # Search for exercises
        self.wait_for_element("#apiSearchInput")
        self.type("#apiSearchInput", "Bench Press")
        self.execute_script("document.querySelector('#manual-pane button.btn-primary[type=button]').click()")
        self.wait_for_element("#searchResults .list-group-item", timeout=15)

        # Add first exercise to staging area
        first_result = self.find_elements("#searchResults .list-group-item")[0]
        self.execute_script("arguments[0].click();", first_result)

        # Fill in staging table inputs
        self.wait_for_element("#stagingTable tbody tr")
        inputs = self.find_elements("#stagingTable tbody tr input")
        for input_el in inputs:
            key = input_el.get_attribute("data-key")
            if key == "sets":
                input_el.clear()
                input_el.send_keys("4")
            elif key == "reps":
                input_el.clear()
                input_el.send_keys("12")
            elif key == "weight_lbs":
                input_el.clear()
                input_el.send_keys("135")
            elif key == "duration_minutes":
                input_el.clear()
                input_el.send_keys("30")
            elif key == "calories_burned":
                input_el.clear()
                input_el.send_keys("200")

        # Save workout session
        self.execute_script("document.querySelector('button.btn-success.btn-lg').click()")
        self.accept_alert()  # confirm save

        # Verify redirect to "My Workouts"
        self.wait_for_url_contains("/workouts/ui", timeout=15)
        self.assert_text("Workout Log", "h2")

    # -------------------------
    # Statistics Tests
    # -------------------------
    def test_charts_display(self):
        """
        Test that the statistics charts display correctly or show a no-data message.
        """
        self.register_and_login()
        self.open(f"{BASE_URL}/stats/ui")
        self.wait_for_element_visible("#calChart", timeout=15)

        # Wait for spinner to disappear
        if self.is_element_present(".spinner"):
            self.wait_for_element_not_visible(".spinner", timeout=20)

        # Verify either chart or no-data message is visible
        if self.is_element_present("#macroChart") and self.is_element_visible("#macroChart"):
            self.assert_element("#macroChart")
        else:
            self.wait_for_element_visible("#noMacroMessage", timeout=10)
            self.assert_element("#noMacroMessage")
