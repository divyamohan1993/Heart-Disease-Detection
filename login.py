# import streamlit as st
# import yaml
# import bcrypt

# # Load user data from config.yaml
# def load_users():
#     with open("config.yaml", "r") as file:
#         config = yaml.safe_load(file)
#     return config.get("credentials", {}).get("usernames", {})

# # Verify password using bcrypt
# def check_password(input_password, hashed_password):
#     return bcrypt.checkpw(input_password.encode(), hashed_password.encode())

# # Login Page
# def login_page():
#     # Custom CSS styling
#     st.markdown("""
#         <style>
#         .login-box {
#             background-color: #f2f2f2;
#             padding: 2rem;
#             border-radius: 1rem;
#             width: 100%;
#             max-width: 400px;
#             margin: auto;
#             margin-top: 30px;
#             box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
#             text-align: center;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     # Image above the login box
#     st.image("Heart.png", width=120)

#     # Login form container
#     st.markdown('<div class="login-box">', unsafe_allow_html=True)

#     st.title("🩺 Doctor Login")
#     username = st.text_input("👨‍⚕️ Username", key="login_username").lower()
#     password = st.text_input("🔒 Password", type="password", key="login_password")


#     users = load_users()
#     login_btn = st.button("Login")

#     if login_btn:
#         if username in users:
#             hashed_pw = users[username]["password"]
#             if check_password(password, hashed_pw):
#                 st.success(f"Welcome Dr. {users[username]['name']} 👋")
#                 st.session_state.logged_in = True
#                 st.session_state.username = username
#             else:
#                 st.error("❌ Incorrect password.")
#         else:
#             st.error("❌ Username not found.")

#     st.markdown('</div>', unsafe_allow_html=True)

# # Run login page
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if not st.session_state.logged_in:
#     login_page()
# else:
#     st.success("✅ You are logged in! Continue to the dashboard.")


# login.py

import streamlit as st
import bcrypt
import sqlite3

DB_FILE = 'submissions.db'

def load_user(username: str):
    """Return (username, name, password_hash) or None if not found."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row

def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def login_page():
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

    st.image("Heart.png", width=120)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)

    st.title("🩺 Doctor Login")
    username = st.text_input("👨‍⚕️ Username", key="login_username").strip().lower()
    password = st.text_input("🔒 Password", type="password", key="login_password")

    if st.button("Login"):
        if not username or not password:
            st.error("❌ Please enter both username and password.")
        else:
            row = load_user(username)
            if row is None:
                st.error("❌ Username not found.")
            else:
                _, name, hashed_pw = row
                if check_password(password, hashed_pw):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.full_name = name
                    st.success(f"Welcome Dr. {name} 👋")
                    # Force a rerun so the app sees logged_in=True immediately:
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect password.")

    st.markdown('</div>', unsafe_allow_html=True)

# Boilerplate: if not logged_in, show login form; else show a message.
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    st.success("✅ You are already logged in. Automatically taking you to the dashboard...") 
    # We will handle redirect in app.py below.
