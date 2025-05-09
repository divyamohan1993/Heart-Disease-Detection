import os
import pickle
import streamlit as st
from streamlit_option_menu import option_menu
import yaml

# Set page configuration
st.set_page_config(page_title="Health Assistant",
                   layout="wide",
                   page_icon="🧑‍⚕️")

# Load the saved models
heart_disease_model = pickle.load(open('heart_disease_model.sav', 'rb'))

# Load user credentials from the config.yaml file
def load_user_credentials():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Sidebar for navigation
with st.sidebar:
    selected = option_menu('Heart Disease Detection System',
                           ['Login', 'Signup', 'Forgot Password', 'Heart Disease Prediction'],
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

# Implement Heart Disease Prediction Page
elif selected == "Heart Disease Prediction":
    # If the user is logged in, allow prediction
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        # page title
        st.title('Heart Disease Prediction using ML')

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
            user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
            user_input = [float(x) for x in user_input]
            heart_prediction = heart_disease_model.predict([user_input])

            if heart_prediction[0] == 1:
                heart_diagnosis = 'The person is having heart disease'
            else:
                heart_diagnosis = 'The person does not have any heart disease'

        st.success(heart_diagnosis)

    else:
        st.warning("Please log in to access the Heart Disease Prediction.")
