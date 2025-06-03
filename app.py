# app.py

import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu

import uuid
from datetime import datetime, timedelta
from io import BytesIO
import sqlite3
import pandas as pd
import zipfile

from fpdf import FPDF

DB_FILE = 'submissions.db'

# ─── 1) Initialize both tables (users + submissions) ──────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users table:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name     TEXT,
            password TEXT
        )
    """)
    # Submissions table:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id        TEXT PRIMARY KEY,
            age       REAL,
            sex       REAL,
            cp        REAL,
            trestbps  REAL,
            chol      REAL,
            fbs       REAL,
            restecg   REAL,
            thalach   REAL,
            exang     REAL,
            oldpeak   REAL,
            slope     REAL,
            ca        REAL,
            thal      REAL,
            diagnosis TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()  # make sure both tables exist

# ─── 2) Submission helpers ────────────────────────────────────────────────────────
def save_submission_db(sub: dict):
    """Insert (or replace) one row into submissions table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO submissions (
            id, age, sex, cp, trestbps, chol, fbs,
            restecg, thalach, exang, oldpeak, slope, ca, thal, diagnosis
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sub['id'],
        float(sub['age']), float(sub['sex']), float(sub['cp']),
        float(sub['trestbps']), float(sub['chol']), float(sub['fbs']),
        float(sub['restecg']), float(sub['thalach']), float(sub['exang']),
        float(sub['oldpeak']), float(sub['slope']), float(sub['ca']),
        float(sub['thal']), sub['diagnosis']
    ))
    conn.commit()
    conn.close()

def generate_patient_id() -> str:
    """
    Generates a sequential ID per day, of form YYYYMMDD_NNN.
    """
    today = datetime.now().strftime("%Y%m%d")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM submissions WHERE id LIKE ?", (f"{today}%",))
    count = cursor.fetchone()[0] + 1
    conn.close()
    return f"{today}_{count:03d}"  # e.g. '20250601_001'

# ─── 3) PDF generator (fpdf2) ──────────────────────────────────────────────────────
def generate_pdf(submission: dict) -> BytesIO:
    """
    Creates a hospital‐style single-page PDF for one submission dict.
    Returns a BytesIO buffer ready for download.
    """
    pdf = FPDF(format='letter')
    pdf.add_page()

    # Convert UTC → IST for timestamp
    now_utc = datetime.utcnow()
    now_ist = now_utc + timedelta(hours=5, minutes=30)

    # HEADER
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(30, 30, 120)
    pdf.cell(0, 10, "Shoolini Health Center", ln=True, align='C')
    pdf.set_font("Helvetica", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Heart Disease Detection Unit", ln=True, align='C')
    pdf.cell(0, 8, 
             "Solan-Oachghat-Kumarhatti Highway, Bajhol, Himachal Pradesh 173229, India",
             ln=True, align='C')
    pdf.cell(0, 8, "Phone: +917207314640 | Email: healthcenter@shooliniuniversity.com",
             ln=True, align='C')
    pdf.ln(10)

    # TITLE + META
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Patient Heart Disease Report", ln=True, align='L')
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 8, f"Date: {now_ist.strftime('%Y-%m-%d %H:%M:%S')} IST", ln=True)
    pdf.cell(0, 8, f"Patient ID: {submission['id']}", ln=True)
    pdf.ln(8)

    # PATIENT INFO
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(0, 10, "Patient Information", ln=True)
    pdf.set_font("Helvetica", '', 10)
    fields = [
        ("Age", submission['age']),
        ("Sex", submission['sex']),
        ("Chest Pain Type", submission['cp']),
        ("Resting Blood Pressure", submission['trestbps']),
        ("Cholesterol", submission['chol']),
        ("Fasting Blood Sugar", submission['fbs']),
        ("Resting ECG", submission['restecg']),
        ("Max Heart Rate", submission['thalach']),
        ("Exercise Induced Angina", submission['exang']),
        ("Oldpeak", submission['oldpeak']),
        ("Slope", submission['slope']),
        ("CA (vessels colored)", submission['ca']),
        ("Thal", submission['thal']),
    ]
    for label, value in fields:
        pdf.cell(0, 8, f"{label}: {value}", ln=True)
    pdf.ln(8)

    # DIAGNOSIS
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(0, 10, "Diagnosis", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 8, submission['diagnosis'])

    # FOOTER
    pdf.set_y(-30)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 
        "This is a computer-generated report. For critical interpretation, consult a certified cardiologist.",
        ln=True, align='C'
    )

    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# ─── 4) Load ML model ────────────────────────────────────────────────────────────
heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))

# ─── 5) Streamlit page config & sidebar menu ─────────────────────────────────────
st.set_page_config(
    page_title="Health Assistant",
    layout="wide",
    page_icon="🧑‍⚕️"
)

with st.sidebar:
    selected = option_menu(
        'Heart Disease Detection System',
        [
            'Login',
            'Signup',
            'Forgot Password',
            'Heart Disease Detection',
            'Bulk Reports',          # new 5th item
        ],
        menu_icon='hospital-fill',
        icons=['key', 'person-add', 'key', 'heart', 'cloud-download'],
        default_index=0
    )

# ─── 6) Auto-redirect if already logged_in and trying to hit Login/Signup/Forgot ──
if st.session_state.get('logged_in', False):
    # If user is already logged in and clicked on any of these, send them to detection:
    if selected in ("Login", "Signup", "Forgot Password"):
        selected = "Heart Disease Detection"

# ─── 7) ROUTING ───────────────────────────────────────────────────────────────────
if selected == "Login":
    import login
    login.login_page()

elif selected == "Signup":
    import signup
    signup.signup_page()

elif selected == "Forgot Password":
    import forgot_password
    forgot_password.forgot_password_page()

elif selected == "Heart Disease Detection":
    # Show the detection page only if logged_in
    if st.session_state.get('logged_in', False):
        st.title('Heart Disease Detection using DL')

        # Generate a new patient ID
        patient_id = generate_patient_id()
        st.markdown(f"**Patient ID:** `{patient_id}`")

        # Input fields (unique key for each)
        col1, col2, col3 = st.columns(3)
        with col1: age     = st.text_input('Age', key='age')
        with col2: sex     = st.text_input('Sex', key='sex')
        with col3: cp      = st.text_input('Chest Pain types', key='cp')
        with col1: trestbps= st.text_input('Resting Blood Pressure', key='trestbps')
        with col2: chol    = st.text_input('Serum Cholestoral in mg/dl', key='chol')
        with col3: fbs     = st.text_input('Fasting Blood Sugar > 120 mg/dl', key='fbs')
        with col1: restecg = st.text_input('Resting Electrocardiographic results', key='restecg')
        with col2: thalach = st.text_input('Maximum Heart Rate achieved', key='thalach')
        with col3: exang   = st.text_input('Exercise Induced Angina', key='exang')
        with col1: oldpeak = st.text_input('ST depression induced by exercise', key='oldpeak')
        with col2: slope   = st.text_input('Slope of the peak exercise ST segment', key='slope')
        with col3: ca      = st.text_input('Major vessels colored by flourosopy', key='ca')
        with col1: thal    = st.text_input(
                            'thal: 0 = normal; 1 = fixed defect; 2 = reversible defect',
                            key='thal'
                         )

        if st.button('Heart Disease Test Result'):
            # Convert inputs to float; if any fail, show error
            try:
                inputs = [float(x) for x in [age, sex, cp, trestbps, chol, fbs,
                                             restecg, thalach, exang, oldpeak,
                                             slope, ca, thal]]
            except Exception:
                st.error("⚠️ All fields must be numeric.")
            else:
                pred = heart_disease_model.predict([inputs])[0]
                diagnosis = (
                    'The person is having heart disease'
                    if pred == 1 else
                    'The person does not have any heart disease'
                )
                st.success(diagnosis)

                # Build submission dict & save to DB
                submission = {
                    'id'     : patient_id,
                    'age'    : age,
                    'sex'    : sex,
                    'cp'     : cp,
                    'trestbps': trestbps,
                    'chol'   : chol,
                    'fbs'    : fbs,
                    'restecg': restecg,
                    'thalach': thalach,
                    'exang'  : exang,
                    'oldpeak': oldpeak,
                    'slope'  : slope,
                    'ca'     : ca,
                    'thal'   : thal,
                    'diagnosis': diagnosis
                }
                save_submission_db(submission)

                # Generate a single-patient PDF
                pdf_buf = generate_pdf(submission)
                st.download_button(
                    "📄 Download Report as PDF",
                    data=pdf_buf,
                    file_name=f"report_{patient_id}.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("⚠️ Please log in to access the Heart Disease Detection.")

elif selected == "Bulk Reports":
    # Bulk CSV → PDF → ZIP
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Please log in first to generate bulk reports.")
    else:
        st.title("📥 Bulk PDF Report Generation")

        st.markdown("""
        Upload a CSV with these columns (in this order):
        
        `age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target`
        
        For each row, we will:
        1. Generate a new `patient_id` (YYYYMMDD_NNN).
        2. Use `target` (0 or 1) to form the diagnosis text.
        3. Build a PDF report.
        4. Bundle ALL generated PDFs into a single ZIP for download.
        """)

        csv_file = st.file_uploader("Upload CSV", type=["csv"])
        if csv_file is not None:
            try:
                df = pd.read_csv(csv_file)
            except Exception as e:
                st.error(f"❌ Failed to parse CSV: {e}")
                st.stop()

            required_cols = [
                'age','sex','cp','trestbps','chol','fbs',
                'restecg','thalach','exang','oldpeak','slope','ca','thal','target'
            ]
            if not all(col in df.columns for col in required_cols):
                st.error(f"❌ CSV must contain these columns (exact names): {required_cols}")
                st.stop()

            # Let user confirm how many records were read
            st.success(f"✅ {len(df)} rows loaded.")

            if st.button("Generate All Reports"):
                with st.spinner("Generating PDFs…"):
                    # Create an in-memory zip
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                        for idx, row in df.iterrows():
                            pid = generate_patient_id()
                            diag_text = (
                                "The person is having heart disease"
                                if int(row['target']) == 1 else
                                "The person does not have any heart disease"
                            )
                            submission = {
                                'id'      : pid,
                                'age'     : row['age'],
                                'sex'     : row['sex'],
                                'cp'      : row['cp'],
                                'trestbps': row['trestbps'],
                                'chol'    : row['chol'],
                                'fbs'     : row['fbs'],
                                'restecg' : row['restecg'],
                                'thalach' : row['thalach'],
                                'exang'   : row['exang'],
                                'oldpeak' : row['oldpeak'],
                                'slope'   : row['slope'],
                                'ca'      : row['ca'],
                                'thal'    : row['thal'],
                                'diagnosis': diag_text
                            }

                            # (Optional) save each bulk record to DB as well:
                            save_submission_db(submission)

                            # generate one PDF
                            buf = generate_pdf(submission)
                            # name: report_<patient_id>.pdf
                            zipf.writestr(f"report_{pid}.pdf", buf.read())

                    zip_buffer.seek(0)
                    st.success("✅ All PDFs generated and zipped.")

                    st.download_button(
                        "📦 Download ZIP of All Reports",
                        data=zip_buffer,
                        file_name=f"bulk_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/x-zip-compressed"
                    )
        else:
            st.info("ℹ️ Please upload a CSV to begin.")

else:
    st.info("Select a menu item from the sidebar.")
