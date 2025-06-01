import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import yaml

## dmj
import uuid
import json
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import sqlite3
###

# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")

## dmj
# DATA_FILE = 'submissions.json'

DB_FILE = 'submissions.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id TEXT PRIMARY KEY,
            age REAL,
            sex REAL,
            cp REAL,
            trestbps REAL,
            chol REAL,
            fbs REAL,
            restecg REAL,
            thalach REAL,
            exang REAL,
            oldpeak REAL,
            slope REAL,
            ca REAL,
            thal REAL,
            diagnosis TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_submission_db(sub: dict):
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

# initialize DB before anything else
init_db()

# def save_submission(submission: dict):
#     # load existing
#     if os.path.exists(DATA_FILE):
#         with open(DATA_FILE, 'r') as f:
#             try: data = json.load(f)
#             except: data = []
#     else:
#         data = []
#     data.append(submission)
#     with open(DATA_FILE, 'w') as f:
#         json.dump(data, f, indent=2)

def generate_patient_id():
    today = datetime.now().strftime("%Y%m%d")  # e.g., '20250601'
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM submissions WHERE id LIKE ?", (f"{today}%",))
    count = cursor.fetchone()[0] + 1
    conn.close()
    return f"{today}_{count:03d}"  # e.g., '20250601_001'


# def generate_pdf(submission: dict) -> BytesIO:
#     """
#     Creates a one-page PDF with all submission fields.
#     Returns a BytesIO buffer for Streamlit download.
#     """
#     pdf = FPDF(format='letter')
#     pdf.add_page()
#     pdf.set_font("Helvetica", size=12)
#     y = 10

#     for k, v in submission.items():
#         pdf.cell(0, 8, f"{k}: {v}", ln=True)
#         y += 8
#         # (FPDF automatically flows to next line)

#     buf = BytesIO()
#     pdf.output(buf)
#     buf.seek(0)
#     return buf

def generate_pdf(submission: dict) -> BytesIO:
    """
    Generates a hospital-style patient report PDF.
    Returns a BytesIO object for download.
    """
    pdf = FPDF(format='letter')
    pdf.add_page()

    # Hospital Header
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_text_color(30, 30, 120)
    pdf.cell(0, 10, "Shoolini Health Center", ln=True, align='C')
    pdf.set_font("Helvetica", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Heart Disease Detection Unit", ln=True, align='C')
    pdf.cell(0, 8, "Solan-Oachghat-Kumarhatti Highway, Bajhol, Himachal Pradesh 173229, India", ln=True, align='C')
    pdf.cell(0, 8, "Phone: +917207314640 | Email: healthcenter@shooliniuniversity.com", ln=True, align='C')
    pdf.ln(10)

    # Report Title
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Patient Heart Disease Report", ln=True, align='L')
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Patient ID: {submission['id']}", ln=True)
    pdf.ln(8)

    # Patient Info Section
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

    # Diagnosis Section
    pdf.set_font("Helvetica", 'B', 13)
    pdf.cell(0, 10, "Diagnosis", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.multi_cell(0, 8, submission['diagnosis'])

    # Footer
    pdf.set_y(-30)
    pdf.set_font("Helvetica", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "This is a computer-generated report from Shoolini Health Center. For any critical interpretation, please consult a certified cardiologist.", ln=True, align='C')

    # Output
    buf = BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

### dmj end


# Load the saved models
heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))

# Load user credentials from the config.yaml file
def load_user_credentials():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Sidebar for navigation
with st.sidebar:
    selected = option_menu('Heart Disease Detection System',
                           ['Login', 'Signup', 'Forgot Password', 'Heart Disease Detection'],
                           menu_icon='hospital-fill',
                           icons=['key', 'person-add', 'key', 'heart'],
                           default_index=0)

# Implement Login Page
if selected == "Login":
    import login
    login.login_page()

# Implement Signup Page
elif selected == "Signup":
    import signup
    signup.signup_page()

# Implement Forgot Password Page
elif selected == "Forgot Password":
    import forgot_password
    forgot_password.forgot_password_page()

# # Implement Heart Disease Detection Page
# elif selected == "Heart Disease Detection":
#     # If the user is logged in, allow prediction
#     if 'logged_in' in st.session_state and st.session_state.logged_in:
#         # page title
#         st.title('Heart Disease Detection using DL')

#         col1, col2, col3 = st.columns(3)

#         with col1:
#             age = st.text_input('Age')

#         with col2:
#             sex = st.text_input('Sex')

#         with col3:
#             cp = st.text_input('Chest Pain types')

#         with col1:
#             trestbps = st.text_input('Resting Blood Pressure')

#         with col2:
#             chol = st.text_input('Serum Cholestoral in mg/dl')

#         with col3:
#             fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl')

#         with col1:
#             restecg = st.text_input('Resting Electrocardiographic results')

#         with col2:
#             thalach = st.text_input('Maximum Heart Rate achieved')

#         with col3:
#             exang = st.text_input('Exercise Induced Angina')

#         with col1:
#             oldpeak = st.text_input('ST depression induced by exercise')

#         with col2:
#             slope = st.text_input('Slope of the peak exercise ST segment')

#         with col3:
#             ca = st.text_input('Major vessels colored by flourosopy')

#         with col1:
#             thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversible defect')

#         # Prediction logic
#         heart_diagnosis = ''

#         if st.button('Heart Disease Test Result'):
#             user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
#             user_input = [float(x) for x in user_input]
#             heart_prediction = heart_disease_model.predict([user_input])

#             if heart_prediction[0] == 1:
#                 heart_diagnosis = 'The person is having heart disease'
#             else:
#                 heart_diagnosis = 'The person does not have any heart disease'

#         st.success(heart_diagnosis)

#     else:
#         st.warning("Please log in to access the Heart Disease Detection.")


## dmj
elif selected == "Heart Disease Detection":
    if st.session_state.get('logged_in'):
        st.title('Heart Disease Detection using DL')

        # generate & show a patient ID
        # patient_id = str(uuid.uuid4())[1::4]
        patient_id = generate_patient_id()
        st.markdown(f"**Patient ID:** `{patient_id}`")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.text_input('Age', key='age')

        with col2:
            sex = st.text_input('Sex', key='sex')

        with col3:
            cp = st.text_input('Chest Pain types', key='cp')

        with col1:
            trestbps = st.text_input('Resting Blood Pressure', key='trestbps')

        with col2:
            chol = st.text_input('Serum Cholestoral in mg/dl', key='chol')

        with col3:
            fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl', key='fbs')

        with col1:
            restecg = st.text_input('Resting Electrocardiographic results', key='restecg')

        with col2:
            thalach = st.text_input('Maximum Heart Rate achieved', key='thalach')

        with col3:
            exang = st.text_input('Exercise Induced Angina', key='exang')

        with col1:
            oldpeak = st.text_input('ST depression induced by exercise', key='oldpeak')

        with col2:
            slope = st.text_input('Slope of the peak exercise ST segment', key='slope')

        with col3:
            ca = st.text_input('Major vessels colored by flourosopy', key='ca')

        with col1:
            thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversible defect', key='thal')


        # Prediction logic
        heart_diagnosis = ''

        if st.button('Heart Disease Test Result'):
            inputs = [float(x) for x in [age, sex, cp, trestbps, chol, fbs,
                                         restecg, thalach, exang, oldpeak,
                                         slope, ca, thal]]
            pred = heart_disease_model.predict([inputs])[0]
            diagnosis = ('The person is having heart disease'
                         if pred==1 else
                         'No heart disease detected')
            st.success(diagnosis)

            # build a record and save it
            submission = {
                'id': patient_id,
                'age': age, 'sex': sex, 'cp': cp,
                'trestbps': trestbps, 'chol': chol,
                'fbs': fbs, 'restecg': restecg,
                'thalach': thalach, 'exang': exang,
                'oldpeak': oldpeak, 'slope': slope,
                'ca': ca, 'thal': thal,
                'diagnosis': diagnosis
            }
            save_submission_db(submission)

            # offer PDF download
            pdf_buf = generate_pdf(submission)
            st.download_button(
                "📄 Download Report as PDF",
                data=pdf_buf,
                file_name=f"report_{patient_id}.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("Please log in to access the Heart Disease Detection.")