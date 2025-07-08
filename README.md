
# Evan AI Budget Tracker  — Smart Budgeting Assistant

An AI-enhanced Flask web app that helps users manage their budget, track expenses, and predict spending using machine learning.

---

## 💡 Overview

**FinSense** (originally named Evan) is a personal finance tracker and assistant powered by Python, Flask, and TensorFlow. It enables users to:

- Register and manage budgets
- Record income and expenses
- Predict future spending patterns using a trained ML model
- Visualize and plan their financial health

---

## 🧰 Features

- 🔐 User registration and login
- 💼 Budget and income tracking
- 📉 Expense entry and history
- 📊 Spending prediction with TensorFlow
- 📆 Calendar-based views and statistics
- 📂 SQL database for data persistence
- 🧪 Unit testing with pytest

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Installation

```bash
git clone https://github.com/your-username/Evan.git
cd Evan
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Run the App

```bash
python app/routes.py
```

Visit: `http://localhost:5000`

---

## 🧠 ML Model

- `spending_model_tf.h5` is a trained model used in `expensePredModel.py` to estimate future expenses based on past data.
- Adjust model or retrain with new datasets for enhanced predictions.

---

## 🧪 Testing

Run unit tests:

```bash
pytest app/test_evan.py
```

---

## 📁 Project Structure

```
Evan/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── dbfunc.py
│   ├── expensePredModel.py
│   ├── templates/
│   ├── static/
│   └── Evan.sql
├── spending_model_tf.h5
└── requirements.txt
```

---

## ✨ Future Improvements

- Add expense category analytics
- Improve dashboard visuals with Plotly or Chart.js
- Export reports to PDF or Excel
- Mobile responsiveness with Bootstrap

---

## 👩‍💻 Author

Developed by **Ana Paula Goncalves**  
AI-powered budgeting assistant created as part of a personal or academic software project.
