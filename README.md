# CSCI 4230 – Advanced Web Development - Final Project
## 💪 LT Fitness Tracker (AI-Powered Fitness App)
### Developers: Shian Li Chen (100813628) & Thanushan Satheeskumar (100784004)

LT Fitness Tracker is a full-stack fitness and nutrition tracker that uses local Artificial Intelligence to generate personalized workout plans and healthy recipes.

**You can check out the live site here: [https://ltfitnesstracker.online](https://ltfitnesstracker.online)**

## 🚀 Features

* **Workout Logger:** Track exercises, sets, reps, and weight.

* **AI Workout Generator:** Ask the AI to create a plan based on your goals (e.g., "Leg day with no equipment").

* **Recipe Cookbook:** Search TheMealDB or ask the "Gourmet" AI for nutritional recipes.

* **Analytics Dashboard:** Visualize your calories burned vs. consumed and macronutrient breakdown.

* **Fully Dockerized:** Runs the Frontend, Backend, Database, and AI Server with a single command.

## 🛠️ Prerequisites

1. **Docker Desktop:** You **must** have Docker Desktop installed and running.
   * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
   * *Note: Ensure the whale icon is visible in your taskbar and says "Engine Running" before starting.*

2. **Hardware Requirements:**
   * Since this app runs AI models locally on your machine, **8GB+ of RAM** is recommended.

## ⚡ Quick Start (The "One Command" Setup)

1. **Clone the Repository:**

   ```bash
   git clone <repo-url>
   cd CSCI4230_Final_Project
   ```

2. **Run the Application:**
   Open your terminal in the project folder and run:

   ```bash
   docker compose up --build
   ```

3. **⚠️ IMPORTANT STEP: Wait for AI Models ⚠️**
   
   Once the command runs, the application will be accessible immediately at `http://localhost:5000`. **However, the AI features will NOT work yet.**

   Docker is automatically downloading two large AI models (`goosedev/luna` and `ALIENTELLIGENCE/gourmetglobetrotter`) in the background.

   * **Check your terminal logs.**
   * You must wait until you see this specific message from the `ltfitnesstracker_model_puller` service:

   ```text
   ltfitnesstracker_model_puller | All models downloaded successfully!
   ltfitnesstracker_model_puller exited with code 0
   ```

   * *This takes 2-10 minutes, depending on your internet speed.*
   * *If you try to use the "Generate Workout" or "AI Chef" buttons before this line appears, the app will use a "Fallback Simulation" (mock data).*

4. **Access the App:**

   * Open your browser to [**http://localhost:5000**](http://localhost:5000), [**http://127.0.0.1:5000**](http://127.0.0.1:5000), or [**http://localhost:80**](http://localhost:80)
      - **Note:** This will depend on the configuration of your terminal and working environment
   * Click **Register** to create a new account (The database starts empty).

## 🌐 Deployment Documentation

The application is deployed live using a containerized approach on a Virtual Private Server (VPS).

### Infrastructure Stack
* **Hosting Provider:** Hostinger (KVM 2 VPS - 8GB RAM to support AI models).
* **Domain Management:** NameCheap (DNS pointed to Hostinger VPS IP).
* **Containerization:** Docker & Docker Compose.
* **Web Server:** Nginx (Reverse Proxy acting as the gateway).
* **SSL/Security:** Certbot (Let's Encrypt) for HTTPS.

### Deployment Process (Steps Taken)

1. **Server Provisioning:**
   * Provisioned an Ubuntu 24.04 VPS on Hostinger.
   * Installed Docker Engine and Docker Compose.

2. **DNS Configuration:**
   * Purchased `ltfitnesstracker.online` via NameCheap.
   * Configured **A Records** in DNS settings to point `@` and `www` to the VPS IP address.

3. **Production Configuration:**
   * Configured `nginx.conf` to reverse proxy traffic from Port 80/443 -> Flask Port 5000.
   * Created a production `.env` file on the server with secure keys and `FLASK_ENV=production`.
   * Set `JWT_COOKIE_SECURE=True` to ensure cookies are only sent over HTTPS.

4. **SSL Certification:**
   * Used the **Certbot** Docker container to generate SSL certificates.
   * Configured Nginx to force redirect all HTTP traffic to HTTPS.

## 🏗️ Architecture

**Chosen Architecture:** Monolithic MVC with modular service containers.  
* The application follows a **Model-View-Controller (MVC)** pattern:
  * **Models:** SQLAlchemy ORM for database models (Users, Workouts, Recipes, Logs, etc.)
  * **Views:** HTML templates with Bootstrap 5 and Chart.js for frontend rendering
  * **Controllers:** Flask routes handling API endpoints and business logic

* **Frontend:** HTML5, Bootstrap 5, Chart.js, Jinja2
* **Backend:** Python Flask (SQLAlchemy, JWT Token Auth, Blueprints)
* **Database:** MySQL 8.0 (Containerized)
* **AI Engine:** Ollama (Containerized)
  * **Workout Model:** `goosedev/luna`
  * **Recipe Model:** `ALIENTELLIGENCE/gourmetglobetrotter`

* **Security Architecture:**
  * JWT Authentication
  * CSRF Protection
  * Encrypted passwords
  * Secure cookies
  * Restricted endpoints

* **Database Design:**
  * SQLAlchemy ORM
  * Foreign-key relational design
  * Structured indexing
  * Migration-safe models

## 🗂️ Database Schema

### Tables Overview

| Table                  | Description |
|------------------------|-------------|
| users                  | Stores user accounts, credentials, roles, and timestamps |
| workouts               | Logs individual workout sessions per user |
| recipes                | Stores user-created recipes with nutritional estimates |
| password_reset_tokens  | Handles secure password reset requests |

---

### Table Definitions

#### users
Stores application users and authentication details.

- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `role`
- `created_at`

---

#### workouts
Stores individual workout entries associated with users.

- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `exercise_name`
- `start_time`
- `end_time`
- `duration_minutes`
- `sets`
- `reps`
- `weight_lbs`
- `machine`
- `calories_burned`
- `notes`
- `created_at`

---

#### recipes
Stores recipes created by users, including estimated nutrition values.

- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `title`
- `ingredients`
- `instructions`
- `image_url`
- `calories`
- `protein`
- `carbs`
- `fats`
- `created_at`

---

#### password_reset_tokens
Stores time-limited password reset tokens for users.

- `id` (Primary Key)
- `user_id` (Foreign Key → users.id, ON DELETE CASCADE)
- `token` (Unique)
- `expires_at`
- `used`

---

### Relationships

- **User → Workouts** (One-to-Many)  
  `workouts.user_id` → `users.id`

- **User → Recipes** (One-to-Many)  
  `recipes.user_id` → `users.id`

- **User → Password Reset Tokens** (One-to-Many)  
  `password_reset_tokens.user_id` → `users.id`  
  *(Cascade delete enabled — tokens are removed when a user is deleted)*

---

### Database Notes

- Foreign key constraints are used to enforce referential integrity.
- Token expiration enforces security for password reset actions.
- Recipe nutritional values are estimated and optional.
- All timestamps use UTC.

---

## ✅ API Enpoints

### Summary Table

| Category        | Method | Endpoint                              | Description                        |
|----------------|--------|--------------------------------------|------------------------------------|
| Auth           | POST   | `/auth/register`                     | Register new user                  |
| Auth           | POST   | `/auth/login`                        | Login and receive JWT + CSRF       |
| Auth           | GET    | `/auth/me`                           | Get logged-in user                 |
| Auth           | GET    | `/auth/csrf-token`                   | Get CSRF token                     |
| Auth           | POST   | `/auth/logout`                       | Logout user                        |
| Auth           | POST   | `/auth/change-password`              | Change current password            |
| Auth           | POST   | `/auth/forgot-password`              | Request password reset             |
| Auth           | POST   | `/auth/reset-password`               | Reset password with token          |
| Workouts       | GET    | `/workouts/`                         | List user workouts                 |
| Workouts       | POST   | `/workouts/`                         | Create workout                     |
| Workouts       | GET    | `/workouts/<id>`                     | Retrieve workout                   |
| Workouts       | PUT    | `/workouts/<id>`                     | Update workout                     |
| Workouts       | DELETE | `/workouts/<id>`                     | Delete workout                     |
| Workouts       | POST   | `/workouts/batch`                    | Insert multiple workouts           |
| Workouts (AI)  | POST   | `/workouts/api/generate-workout`     | Generate workout with AI           |
| Workouts (API) | GET    | `/workouts/api/search-exercises`     | Search exercise API                |
| Recipes        | GET    | `/recipes/`                          | List saved recipes                 |
| Recipes        | POST   | `/recipes/`                          | Save recipe                        |
| Recipes        | DELETE | `/recipes/<id>`                     | Delete recipe                      |
| Recipes (AI)   | POST   | `/recipes/api/generate-ai`           | Generate recipe with AI            |
| Recipes (API)  | GET    | `/recipes/api/search-external`       | Search external recipe API         |
| Stats          | GET    | `/stats/api/data`                    | Retrieve charts data  

---

### 🔐 Authentication Endpoints

#### POST `/auth/register`
Registers a new user account.

---

#### POST `/auth/login`
Authenticates the user and sets JWT cookie and CSRF token.

---

#### GET `/auth/me`
Returns current authenticated user.

---

#### GET `/auth/csrf-token`
Issues CSRF token for secured requests.

---

#### POST `/auth/logout`
Logs the user out (invalidates JWT).

> Requires `X-CSRF-TOKEN`

---

#### POST `/auth/change-password`
Changes the user password.

---

#### POST `/auth/forgot-password`
Sends password reset email if user exists.

---

#### POST `/auth/reset-password`
Completes password reset via token.

---

### 🏋️ Workout Endpoints

#### GET `/workouts/`
Returns all workouts for authenticated user.

---

#### POST `/workouts/`
Creates new workout.

---

#### GET `/workouts/<id>`
Retrieve workout details.

---

#### PUT `/workouts/<id>`
Updates existing workout.

> Requires CSRF

---

#### DELETE `/workouts/<id>`
Deletes workout.

> Requires CSRF

---

#### POST `/workouts/batch`
Bulk insert workouts.

---

#### POST `/workouts/api/generate-workout`
Generates a workout using AI.

---

#### GET `/workouts/api/search-exercises`
Exercise API search with fallback.

---

### 🍲 Recipe Endpoints

#### GET `/recipes/`
Fetch saved recipes.

---

#### POST `/recipes/`
Save new recipe.

---

#### DELETE `/recipes/<id>`
Delete recipe.

> Requires CSRF

---

#### POST `/recipes/api/generate-ai`
Generate AI recipe.

---

#### GET `/recipes/api/search-external`
Search external recipe source.

---

### 📊 Statistics

#### GET `/stats/api/data`
Provides:
- Calories burned
- Calories consumed
- Macronutrients

---

### API Endpoint Notes

- JWT-based authentication (cookies)
- CSRF protection on state-changing routes
- All protected routes require valid auth cookie

---

## ❓ Troubleshooting

* **"Exercise Search returns limited results" or "External API Failed":**
  * The external API provider (API Ninjas) frequently disables the free tier for the Exercises endpoint ("This endpoint is currently down for free users").
  * When this happens, the app automatically switches to Local Fallback Mode. You will still see search results, but they are limited to a curated list of common exercises (e.g., Bench Press, Squats, Running) to ensure the app remains usable for demos.

* **"Ports are not available":**
  * This means you have a local MySQL running on port 3306. Stop your local MySQL service or edit `docker-compose.yml` to map ports differently (e.g., `3307:3306`).

* **"Docker DesktopLinuxEngine... system cannot find the file":**
  * Docker Desktop is not running. Open the Docker Desktop app and wait for the green status bar.

* **"Forgot Password Functionality not working":**
  * User needs to be registered and the email you are entering into the forgot password page needs to be in the database user table. If the email is not found in the database table the email will not send. 
