# CSCI 4230 – Advanced Web Development
## Final Project
### Authors: Shian Li Chen (100813628), Thanushan Satheeskumar (100784004)

# 🌙 LT Fitness Tracker - AI-Powered Fitness App

LT Fitness Tracker is a full-stack fitness and nutrition tracker that uses local Artificial Intelligence to generate personalized workout plans and healthy recipes.

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

   \`\`\`bash
   git clone <your-repo-url>
   cd CSCI4230_Final_Project
   \`\`\`

2. **Run the Application:**
   Open your terminal in the project folder and run:

   \`\`\`bash
   docker compose up --build
   \`\`\`

3. **⚠️ CRITICAL STEP: Wait for AI Models ⚠️**
   
   Once the command runs, the application will be accessible immediately at \`http://localhost:5000\`. **However, the AI features will NOT work yet.**

   Docker is automatically downloading two large AI models (\`goosedev/luna\` and \`gourmetglobetrotter\`) in the background.

   * **Check your terminal logs.**
   * You must wait until you see this specific message from the \`lunafit_model_puller\` service:

   \`\`\`text
   lunafit_model_puller | All models downloaded successfully!
   lunafit_model_puller exited with code 0
   \`\`\`

   * *This takes 2-10 minutes depending on your internet speed.*
   * *If you try to use the "Generate Workout" or "AI Chef" buttons before this line appears, the app will use a "Fallback Simulation" (mock data).*

4. **Access the App:**

   * Open your browser to: [**http://localhost:5000**](http://localhost:5000)
   * Click **Register** to create a new account (The database starts empty).

## 🏗️ Architecture

* **Frontend:** HTML5, Bootstrap 5, Chart.js
* **Backend:** Python Flask (SQLAlchemy, JWT Auth)
* **Database:** MySQL 8.0 (Containerized)
* **AI Engine:** Ollama (Containerized)
  * **Workout Model:** \`goosedev/luna\`
  * **Recipe Model:** \`ALIENTELLIGENCE/gourmetglobetrotter\`

## ❓ Troubleshooting

* **"Ports are not available":**
  * This means you have a local MySQL running on port 3306. Stop your local MySQL service or edit \`docker-compose.yml\` to map ports differently (e.g., \`3307:3306\`).

* **"Docker DesktopLinuxEngine... system cannot find the file":**
  * Docker Desktop is not running. Open the Docker Desktop app and wait for the green status bar.
