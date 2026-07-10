import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import time
import os

# Page Configuration
st.set_page_config(page_title="Smart Lender AI Pro", page_icon="🏦", layout="wide")

# Advanced Futuristic Glassmorphism CSS with High Visibility Text Fix
st.markdown("""
<style>
@import url('https://googleapis.com');

/* Global Styles */
html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #ffffff !important;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 100%);
}

/* Header Section */
.hero-container {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
}
.big-title {
    font-size: 45px;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}
.sub-title {
    font-size: 18px;
    color: #94a3b8 !important;
    font-weight: 400;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    margin-bottom: 25px;
}
.section-header {
    font-size: 20px;
    font-weight: 600;
    color: #38bdf8 !important;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid rgba(56, 189, 248, 0.2);
    padding-bottom: 8px;
}

/* TEXT VISIBILITY FIX FOR STREAMLIT INPUTS */
label p {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 15px !important;
}

/* Dropdown (Selectbox) Text Color Fix */
div[data-baseweb="select"] * {
    color: #ffffff !important;
    background-color: transparent !important;
}
div[role="listbox"] ul li {
    color: #ffffff !important;
    background-color: #1e293b !important;
}
div[role="listbox"] ul li:hover {
    background-color: #38bdf8 !important;
    color: #020617 !important;
}

/* Number Input Text Color Fix */
input[type="number"] {
    color: #ffffff !important;
    background-color: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Radio Button Text Color Fix */
div[role="radiogroup"] label {
    color: #ffffff !important;
}

/* Prediction Results */
.result-card {
    padding: 35px;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-top: 25px;
}
.approved-ui {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.25) 100%);
    border: 2px solid #10b981;
    box-shadow: 0 0 40px rgba(16, 185, 129, 0.2);
}
.approved-title {
    color: #34d399 !important;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 1px;
}
.rejected-ui {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.25) 100%);
    border: 2px solid #ef4444;
    box-shadow: 0 0 40px rgba(239, 68, 68, 0.2);
}
.rejected-title {
    color: #f87171 !important;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 1px;
}

/* Custom Metrics */
.custom-metric {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 15px;
    margin-top: 20px;
    display: inline-block;
    min-width: 200px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #a78bfa !important;
}
.metric-label {
    font-size: 12px;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# Load AI Model & Scaler
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, 'smart_lender_xgb.pkl')
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.error("❌ Model or Scaler file missing in root directory!")
        st.stop()
        
    model = pickle.load(open(model_path, 'rb'))
    scaler = pickle.load(open(scaler_path, 'rb'))
    return model, scaler

model, scaler = load_model()

# Database Config
DB_PATH = "/data/applicants.db" if os.path.exists("/data") else "applicants.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS loan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gender TEXT, married TEXT, dependents INTEGER,
            education TEXT, self_emp TEXT,
            income REAL, co_income REAL, loan_amount REAL,
            term REAL, credit_history TEXT,
            property_area TEXT, prediction_result TEXT)''')
        conn.commit()
        conn.close()
        return True
    except:
        return False

db_enabled = init_db()

# Title Hero Section
st.markdown("""
<div class='hero-container'>
    <div class='big-title'>🏦 SMART LENDER AI PRO</div>
    <div class='sub-title'>Next-Generation Institutional Loan Underwriting & Risk Analysis System</div>
</div>
""", unsafe_allow_html=True)

# Main Form Container
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='section-header'>👤 Personal Profile</div>", unsafe_allow_html=True)
    gender = st.selectbox("Gender", ["Male", "Female"])
    married = st.selectbox("Marital Status", ["Yes", "No"])
    dependents = st.slider("Number of Dependents", 0, 3, 0)

with col2:
    st.markdown("<div class='section-header'>💼 Employment & Tenure</div>", unsafe_allow_html=True)
    education = st.selectbox("Education Level", ["Graduate", "Not Graduate"])
    self_emp = st.selectbox("Self Employed?", ["No", "Yes"])
    property_area = st.selectbox("Property Demographics", ["Urban", "Semiurban", "Rural"])

with col3:
    st.markdown("<div class='section-header'>💰 Financial Metrics</div>", unsafe_allow_html=True)
    income = st.number_input("Applicant Monthly Income (₹)", value=50000, step=5000)
    co_income = st.number_input("Coapplicant Monthly Income (₹)", value=0, step=5000)
    amount = st.number_input("Requested Loan Amount (₹)", value=200000, step=10000)
    term = st.number_input("Loan Term (In Months)", value=360, step=12)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>📊 Risk Parameters</div>", unsafe_allow_html=True)
credit = st.radio("Bureau Credit History Status", ["1 - Clean Record / Good", "0 - Delinquency Risk / Bad"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

# Elegant Action Button
predict_btn = st.button("🚀 EXECUTE AI RISK UNDERWRITING", use_container_width=True, type="primary")

# Result Placeholder Location
result_placeholder = st.empty()

if predict_btn:
    with st.spinner('AI Engine running predictive risk matrix...'):
        time.sleep(1.2)
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress.progress(i + 1)
        progress.empty()

    # Data transformation
    gender_n = 1 if gender == "Male" else 0
    married_n = 1 if married == "Yes" else 0
    dependents_n = dependents
    education_n = 0 if education == "Graduate" else 1
    self_emp_n = 1 if self_emp == "Yes" else 0
    credit_n = 1 if "1" in credit else 0
    property_map = {"Rural": 0, "Semiurban": 1, "Urban": 2}
    property_n = property_map[property_area]

    raw_inputs = [[gender_n, married_n, dependents_n, education_n, self_emp_n, income, co_income, amount, term, credit_n, property_n]]
    columns = ['Gender','Married','Dependents','Education','Self_Employed','ApplicantIncome','CoapplicantIncome','LoanAmount','Loan_Amount_Term','Credit_History','Property_Area']
    df_input = pd.DataFrame(raw_inputs, columns=columns)
    
    # AI Predictions
    scaled_inputs = scaler.transform(df_input)
    prediction = model.predict(scaled_inputs)
    proba = model.predict_proba(scaled_inputs)[prediction]
    confidence = round(proba * 100, 2)

    # UI Rendering based on Results
    with result_placeholder.container():
        if prediction == 1:
            st.markdown(f"""
            <div class='result-card approved-ui'>
                <div class='approved-title'>🎉 APPLICATION APPROVED</div>
                <p style='color: #a7f3d0; margin-top:10px;'>This profile complies safely with all institutional credit risk matrices.</p>
                <div class='custom-metric'>
                    <div class='metric-value'>{confidence}%</div>
                    <div class='metric-label'>AI Confidence Score</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            result_str = "APPROVED ✅"
        else:
            st.markdown(f"""
            <div class='result-card rejected-ui'>
                <div class='rejected-title'>❌ APPLICATION DECLINED</div>
                <p style='color: #fca5a5; margin-top:10px;'>High underwriting risk detected. Profile does not meet credit benchmarks.</p>
                <div class='custom-metric'>
                    <div class='metric-value'>{confidence}%</div>
                    <div class='metric-label'>AI Risk Confidence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            result_str = "REJECTED ❌"

    # Database logging
    if db_enabled:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO loan_logs 
                (gender, married, dependents, education, self_emp, income, co_income, loan_amount, term, credit_history, property_area, prediction_result) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 

