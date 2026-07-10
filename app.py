import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import time
import os

st.set_page_config(page_title="Smart Lender AI Pro", page_icon="🏦", layout="wide")

# Advanced Glassmorphism CSS with Inputs Font Color Fix
st.markdown("""
<style>
@import url('https://googleapis.com');

/* Main App Layout */
html, body {
    font-family: 'Outfit', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);
}

/* UI Structure */
.glass {
    background: rgba(30, 41, 59, 0.4); 
    backdrop-filter: blur(12px); 
    border: 1px solid rgba(148, 163, 184, 0.2); 
    border-radius: 20px; 
    padding: 25px; 
    margin-bottom: 15px;
}
.big-title {
    font-size: 45px; 
    font-weight: 700; 
    background: linear-gradient(90deg, #38bdf8, #a78bfa); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    text-align: center;
    margin-bottom: 5px;
}

/* CRITICAL FIX: LABELS AND INPUT FONTS VISIBILITY */
/* Input Field Labels (Main Labels) */
label p {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 15px !important;
}

/* Dropdown (Selectbox) Inner Text Fix */
div[data-baseweb="select"] div {
    color: #0f172a !important; /* బాక్స్ లోపల అక్షరాలు ముదురు నలుపు రంగులోకి మారతాయి */
    font-weight: 500 !important;
}

/* Dropdown Options List Text Fix */
div[role="listbox"] ul li {
    color: #ffffff !important;
    background-color: #1e293b !important;
}
div[role="listbox"] ul li:hover {
    background-color: #38bdf8 !important;
    color: #020617 !important;
}

/* Number Input Text Fix */
input[type="number"] {
    color: #ffffff !important; /* నంబర్ టైప్ చేసే అక్షరాలు వైట్ కలర్ */
    background-color: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(148, 163, 184, 0.3) !important;
}

/* Radio Button Text Fix */
div[role="radiogroup"] label p {
    color: #ffffff !important;
}

/* Metric text fix */
div[data-testid="stMetricValue"] div {
    color: #ffffff !important;
}
div[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
}

/* Results Custom Cards */
.approved {
    background: linear-gradient(135deg, #22c55e, #16a34a); 
    padding: 30px; 
    border-radius: 20px; 
    color: white !important; 
    font-size: 32px; 
    font-weight: 700; 
    text-align: center; 
    box-shadow: 0 0 30px rgba(34, 197, 94, 0.6);
}
.rejected {
    background: linear-gradient(135deg, #ef4444, #dc2626); 
    padding: 30px; 
    border-radius: 20px; 
    color: white !important; 
    font-size: 32px; 
    font-weight: 700; 
    text-align: center; 
    box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);
}
</style>
""", unsafe_allow_html=True)

# Safe Model Loading
@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, 'smart_lender_xgb.pkl')
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        st.error("❌ Model or Scaler file missing!")
        st.stop()
        
    try:
        model = pickle.load(open(model_path, 'rb'))
        scaler = pickle.load(open(scaler_path, 'rb'))
        return model, scaler
    except Exception as e:
        st.error(f"⚠️ Model Compatibility Error: {e}")
        st.stop()

model, scaler = load_model()

# DB Path configuration
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

# App Headers
st.markdown("<h1 class='big-title'>🏦 Smart Lender AI Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:16px;'>Next-Gen Institutional Underwriting System</p>", unsafe_allow_html=True)

# FORM
st.markdown("<div class='glass'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👤 Personal")
    gender = st.selectbox("Gender", ["Male", "Female"])
    married = st.selectbox("Married", ["Yes", "No"])
    dependents = st.slider("Dependents", 0, 3, 0)

with col2:
    st.markdown("### 💼 Job & Education")
    education = st.selectbox("Education", ["Graduate", "Not Graduate"])
    self_emp = st.selectbox("Self Employed", ["Yes", "No"])
    property_area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])

with col3:
    st.markdown("### 💰 Finance")
    income = st.number_input("Applicant Income ₹", value=50000, step=5000)
    co_income = st.number_input("Coapplicant Income ₹", value=0, step=5000)
    amount = st.number_input("Loan Amount ₹", value=200000, step=10000)
    term = st.number_input("Term Months", value=360, step=12)

credit = st.radio("Credit History", ["1 - Good", "0 - Bad"], horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

predict_btn = st.button("🚀 Run AI Prediction", use_container_width=True, type="primary")

# RESULT SECTION
result_placeholder = st.empty()

if predict_btn:
    with st.spinner('AI is analyzing your application...'):
        time.sleep(1.2)
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress.progress(i + 1)
        progress.empty()

    # Inputs processing
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
    
    scaled_inputs = scaler.transform(df_input)
    prediction = model.predict(scaled_inputs)[0]
    proba = model.predict_proba(scaled_inputs)[0][prediction]

    result = "APPROVED ✅" if prediction == 1 else "REJECTED ❌"
    confidence = round(proba * 100, 2)

    with result_placeholder.container():
        st.markdown("---")
        st.markdown("### 📊 Prediction Result")
        if "APPROVED" in result:
            st.markdown(f"<div class='approved'>{result}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='rejected'>{result}</div>", unsafe_allow_html=True)
        st.metric("AI Confidence", f"{confidence}%")

    # SAVE TO DB
    if db_enabled:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO loan_logs 
                (gender, married, dependents, education, self_emp, income, co_income, loan_amount, term, credit_history, property_area, prediction_result) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (gender, married, dependents, education, self_emp, income, co_income, amount, term, credit, property_area, result))
            conn.commit()
            conn.close()
        except:
            pass
