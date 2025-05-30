import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import yaml

## dmj
import uuid
import json
from io import BytesIO
from reportlab.pdfgen import canvas
###

# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")

## dmj
DATA_FILE = 'submissions.json'

def save_submission(submission: dict):
    # load existing
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: data = json.load(f)
            except: data = []
    else:
        data = []
    data.append(submission)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_pdf(submission: dict) -> BytesIO:
    buf = BytesIO()
    p = canvas.Canvas(buf)
    p.setFont("Helvetica", 12)
    y = 800
    for k, v in submission.items():
        p.drawString(50, y, f"{k}: {v}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.showPage()
    p.save()
    buf.seek(0)
    return buf
###


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
        patient_id = str(uuid.uuid4())
        st.markdown(f"**Patient ID:** `{patient_id}`")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.text_input('Age')

        with col2:
            sex = st.text_input('Sex')

        with col3:
            cp = st.text_input('Chest Pain types')

        with col1:
            trestbps = st.text_input('Resting Blood Pressure')

        with col2:
            chol = st.text_input('Serum Cholestoral in mg/dl')

        with col3:
            fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl')

        with col1:
            restecg = st.text_input('Resting Electrocardiographic results')

        with col2:
            thalach = st.text_input('Maximum Heart Rate achieved')

        with col3:
            exang = st.text_input('Exercise Induced Angina')

        with col1:
            oldpeak = st.text_input('ST depression induced by exercise')

        with col2:
            slope = st.text_input('Slope of the peak exercise ST segment')

        with col3:
            ca = st.text_input('Major vessels colored by flourosopy')

        with col1:
            thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversible defect')

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
            save_submission(submission)

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