import streamlit as st
import yaml
import bcrypt

# Load user data from config.yaml
def load_users():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config.get("credentials", {}).get("usernames", {})

# Verify password using bcrypt
def check_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

# Login Page
def login_page():
    # Custom CSS styling
    st.markdown("""
        <style>
        .login-box {
            background-color: #f2f2f2;
            padding: 2rem;
            border-radius: 1rem;
            width: 100%;
            max-width: 400px;
            margin: auto;
            margin-top: 30px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Image above the login box
    st.image("Heart.png", width=120)

    # Login form container
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.title("🩺 Doctor Login")
    username = st.text_input("👨‍⚕️ Username")
    password = st.text_input("🔒 Password", type="password")

    users = load_users()
    login_btn = st.button("Login")

    if login_btn:
        if username in users:
            hashed_pw = users[username]["password"]
            if check_password(password, hashed_pw):
                st.success(f"Welcome Dr. {users[username]['name']} 👋")
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("❌ Incorrect password.")
        else:
            st.error("❌ Username not found.")

    st.markdown('</div>', unsafe_allow_html=True)

# Run login page
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    st.success("✅ You are logged in! Continue to the dashboard.")
