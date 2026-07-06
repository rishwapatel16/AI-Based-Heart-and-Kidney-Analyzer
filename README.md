# 🩺 AI-Based Heart and Kidney Analyzer

An AI-powered healthcare web application that predicts the risk of **Heart Disease** and **Kidney Disease** using Machine Learning. The system analyzes medical parameters, calculates a risk percentage, classifies the risk level, and provides personalized health suggestions.

---

## 📌 Project Overview

The AI-Based Heart and Kidney Analyzer is a Flask-based web application developed to assist in the early detection of heart and kidney diseases using Machine Learning.

The application analyzes important medical parameters such as:

- Age
- Blood Pressure
- Cholesterol
- Blood Sugar
- ECG Results
- Maximum Heart Rate
- Exercise Induced Angina
- Serum Creatinine
- Hemoglobin
- Other clinical parameters

Based on the user's input, the system predicts disease risk using the **Random Forest Algorithm** and displays:

- Risk Percentage
- Risk Level (Low, Moderate, High)
- Personalized Health Suggestions

The application also stores prediction history, generates graphical reports, and allows users to download PDF reports.

---

## 🎯 Objectives

- Predict Heart Disease Risk
- Predict Kidney Disease Risk
- Generate Percentage-Based Risk Prediction
- Provide Health Recommendations
- Maintain Prediction History
- Visualize Health Trends
- Generate Downloadable PDF Reports
- Increase Health Awareness using AI

---

## ✨ Features

- User Registration & Login
- Heart Disease Prediction
- Kidney Disease Prediction
- Percentage-Based Risk Analysis
- Risk Categorization (Low, Moderate, High)
- Personalized Health Suggestions
- Prediction History
- Graphical Analysis
- Download PDF Reports
- SQLite Database Integration
- Responsive User Interface

---

## 🛠️ Technologies Used

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- Flask

### Machine Learning

- Scikit-learn
- Random Forest Algorithm

### Database

- SQLite

### Development Tools

- PyCharm
- Git
- GitHub

---

## 🧠 Machine Learning Model

Algorithm Used:

- Random Forest Classifier

The model predicts the probability of disease based on medical parameters and converts the output into:

- Low Risk
- Moderate Risk
- High Risk

along with a percentage score.

---

## 📂 Project Structure

```text
AI-Based-Heart-and-Kidney-Analyzer/
│
├── static/
├── templates/
├── models/
├── database/
├── reports/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/rishwapatel16/AI-Based-Heart-and-Kidney-Analyzer.git
```

### Go to Project Folder

```bash
cd AI-Based-Heart-and-Kidney-Analyzer
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Run the Project

```bash
python app.py
```

---

## 📊 Prediction Workflow

1. User enters medical information.
2. Flask receives the input.
3. The Random Forest model processes the data.
4. Disease probability is calculated.
5. Risk percentage is generated.
6. Risk level is displayed.
7. Health suggestions are provided.
8. Prediction is stored in SQLite.
9. User can view graphs and download a PDF report.

---

## 📷 Screenshots

### Home Page

(Add Screenshot Here)

### Heart Prediction

(Add Screenshot Here)

### Kidney Prediction

(Add Screenshot Here)

### Dashboard

(Add Screenshot Here)

### Prediction History

(Add Screenshot Here)

### Graph Analysis

(Add Screenshot Here)

### PDF Report

(Add Screenshot Here)

---

## 📈 Future Enhancements

- Support additional diseases
- Doctor Consultation Module
- Real-Time Health Monitoring
- Cloud Database Integration
- Mobile Application
- Email Notifications
- AI Chatbot for Health Assistance
- Integration with Wearable Devices

---

## ⚠️ Limitations

- Prediction depends on the quality of input data.
- Limited to Heart and Kidney disease prediction.
- Cannot replace professional medical diagnosis.
- Uses selected medical parameters only.
- No real-time doctor consultation.

---

## 👨‍💻 Developer

**Rishwa Patel**

Bachelor of Engineering (Computer Engineering)

Vishwakarma Government Engineering College (VGEC)

---

## 📄 License

This project is developed for educational and internship purposes.