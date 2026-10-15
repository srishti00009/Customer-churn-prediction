# 📉 ChurnGuard AI

**Customer Churn Prediction & Retention System**

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange?logo=scikit-learn)

## 📋 Overview

ChurnGuard AI is a machine learning-powered web application that provides intelligent predictions and analytics through a modern web interface. The backend is built with **FastAPI** and the frontend uses **vanilla HTML, CSS, and JavaScript** for a responsive, professional UI.

This project is **fully self-contained** with its own authentication database, trained ML models, and frontend assets — no external dependencies outside of this folder.

## 🏗️ Project Structure

```
customer-chrun-prediction/
├── main.py              # FastAPI backend server
├── auth_db.py           # Local authentication database (SQLite)
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── data/
│   └── users.db         # User database (auto-created)
├── frontend/
│   ├── index.html       # Single-page application
│   ├── css/
│   │   └── style.css    # Modern responsive styles
│   └── js/
│       └── app.js       # Application logic
├── utils/
│   └── predictor.py     # ML prediction logic
├── training/
│   ├── train.py         # Model training script
│   └── evaluate.py      # Model evaluation
├── models/              # Trained models (joblib)
└── assets/              # Training datasets
```

## ✨ Features

- **User Authentication** — Register/login with secure password hashing
- **ML Real-time predictions** — Accurate predictions using trained scikit-learn models
- **Interactive Forms** — Tabbed input forms with sliders, selects, and radio buttons
- **Rich Visualizations** — Canvas-based gauges, pie charts, bar charts, and trend lines
- **History Tracking** — In-browser predictions history with CSV export
- **Dark/Light Theme** — Toggle between dark and light mode
- **Responsive Design** — Works on desktop and mobile devices
- **Self-Contained** — No external API dependencies, everything runs locally

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- uv (optional, for faster dependency management)

### Installation & Setup

#### Option 1: Using uv (Recommended)

```bash
# Install uv if you haven't already
pip install uv

# Navigate to the project folder
cd customer-chrun-prediction

# Create a virtual environment
uv venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Train the model (if not already trained)
python training/train.py

# Start the application
python main.py
```

#### Option 2: Using pip

```bash
# Navigate to the project folder
cd customer-chrun-prediction

# Create a virtual environment
python -m venv .venv

# Activate the environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the model (if not already trained)
python training/train.py

# Start the application
python main.py
```

### Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

## 🧠 Machine Learning Model

| Detail | Value |
|--------|-------|
| **Algorithm** | Logistic Regression |
| **Type** | Classification |
| **Framework** | scikit-learn |
| **Training** | Run `python training/train.py` |
| **Evaluation** | Run `python training/evaluate.py` |

### Retraining the Model

To retrain the model with updated data:

```bash
python training/train.py
```

This will:
1. Load the dataset from `assets/data.csv`
2. Preprocess features and scale them
3. Train a new Logistic Regression model
4. Save the model to `models/` directory
5. Generate evaluation metrics and visualizations

## 🖥️ API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|:---:|
| POST | `/api/auth/register` | Register a new user | ❌ |
| POST | `/api/auth/login` | Login and get token | ❌ |
| POST | `/api/predict` | Make a prediction | ✅ |
| GET | `/api/dashboard/metrics` | Get model performance metrics | ✅ |
| GET | `/*` | Serve frontend static files | ❌ |

### Authentication

The API uses token-based authentication. After logging in via `/api/auth/login`, include the token in the `Authorization` header:

```http
Authorization: Bearer <your-token>
```

### Example API Call

```python
import requests

# Login
res = requests.post("http://localhost:8000/api/auth/login", json={
    "username": "testuser",
    "password": "testpass"
})
token = res.json()["token"]

# Make a prediction
headers = {"Authorization": f"Bearer {token}"}
data = {...}  # Feature values
res = requests.post("/api/predict", json=data, headers=headers)
print(res.json())
```

## 🎨 Frontend

The frontend is a single-page application built with vanilla HTML, CSS, and JavaScript:

- **HTML** — Semantic structure with landing, auth, and app views
- **CSS** — Modern design with CSS variables, glassmorphism, and responsive layout
- **JavaScript** — Vanilla JS with async/await for API calls, Canvas API for charts

### Design Highlights

- **Glassmorphism** — Frosted glass card effects with backdrop blur
- **CSS Variables** — Dynamic theming with dark/light mode support
- **Canvas Charts** — Custom-drawn gauges, pie charts, bar charts, and trend lines
- **Animations** — Smooth transitions, hover effects, and fade-in animations
- **Responsive** — Adapts to mobile, tablet, and desktop screens

## 🔧 Troubleshooting

### "Model not found" Error

Run the training script first:
```bash
python training/train.py
```

### Port Already in Use

Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change 8000 to 8001
```

### Database Issues

Delete the database file and restart:
```bash
rm data/users.db  # or del data\users.db on Windows
python main.py
```

## 📝 License

This project is for educational purposes. Feel free to modify and adapt.

---
Built with ❤️ using FastAPI & Scikit-learn
