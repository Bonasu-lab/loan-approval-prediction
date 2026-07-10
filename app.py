import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import time
import os

st.set_page_config(page_title="Smart Lender AI", page_icon="🏦", layout="wide")

# Premium Glass CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap');
html, body, [class*="st-"] {font-family: 'Outfit', sans-serif;}
.stApp {background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #1e293b 100%);}
.glass {background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 20px; padding: 20px; margin-bottom: 15px;}
.big-title {font-size: 42px; font-weight: 700; background: linear-gradient(90deg, #38bdf8, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center;}
.approved {background: linear-gradient(135deg, #22c55e, #16a34a); padding: 30px; border-radius: 20px; color: white; font-size: 32px; font-weight: 700; text-align: center; box-shadow: 0 0 30px rgba(34, 197, 94, 0.6);}
.rejected {background: linear-gradient(135deg, #ef4444, #dc2626); padding: 30px; border-radius: 20px; color: white; font-size: 32px; font-weight: 700; text-align: center; box-shadow: 0 0 30px rgba(239, 68, 68, 0.6);}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, 'smart_lender_xgb.pkl')
    scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
    model = pickle.load(open(model_path, 'rb'))
    scaler = pickle.load(open(scaler_path, 'rb'))
    return model, scaler

model, scaler = load_model()

# FIX: Render Disk use chesthe /data folder lo save avtundi
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
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False

db_enabled = init_db()

st.markdown("<h1 class='big-title'>🏦 Smart Lender AI Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8;'>Next-Gen Loan Approval System</p>", unsafe_allow_html=True)

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
        time.sleep(1.5)
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

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

    # SAVE TO DB - FIX: 12? undali
    if db_enabled:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO loan_logs
            (gender, married, dependents, education, self_emp, income, co_income, loan_amount, term
