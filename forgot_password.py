# import streamlit as st
# import yaml
# import bcrypt

# # Load user data from config.yaml
# def load_users():
#     try:
#         with open("config.yaml", "r") as file:
#             config = yaml.safe_load(file)
#         return config.get("credentials", {}).get("usernames", {})
#     except FileNotFoundError:
#         return {}

# # Save user data to config.yaml
# def save_user(username, hashed_password):
#     users = load_users()

#     # Update the password for the user
#     users[username]["password"] = hashed_password

#     # Save the updated users dictionary to config.yaml
#     with open("config.yaml", "w") as file:
#         yaml.dump({"credentials": {"usernames": users}}, file)

# # Forgot Password Page
# def forgot_password_page():
#     st.markdown("""
#         <style>
#         .forgot-password-box {
#             background-color: #f2f2f2;
#             padding: 2rem;
#             border-radius: 1rem;
#             width: 100%;
#             max-width: 400px;
#             margin: auto;
#             margin-top: 100px;
#             box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     st.markdown('<div class="forgot-password-box">', unsafe_allow_html=True)

#     st.title("🔑 Forgot Password")
#     username = st.text_input("👨‍⚕️ Username")
#     new_password = st.text_input("🔒 New Password", type="password")
#     confirm_password = st.text_input("🔐 Confirm New Password", type="password")

#     if st.button("Reset Password"):
#         users = load_users()

#         if username in users:
#             if new_password == confirm_password:
#                 # Hash the new password
#                 hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

#                 # Save the new password for the user
#                 save_user(username, hashed_pw)
#                 st.success("🎉 Password has been reset successfully! Please login with your new password.")
#             else:
#                 st.error("❌ The passwords do not match.")
#         else:
#             st.error("❌ Username not found.")

#     st.markdown('</div>', unsafe_allow_html=True)

# # Run Forgot Password page
# forgot_password_page()


# forgot_password.py

import streamlit as st
import bcrypt
import sqlite3

DB_FILE = 'submissions.db'

def load_user(username: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row  # either a tuple or None

def update_password(username: str, hashed_pw: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_pw, username))
    conn.commit()
    conn.close()

def forgot_password_page():
    st.markdown("""
        <style>
        .forgot-password-box {
            background-color: #f2f2f2;
            padding: 2rem;
            border-radius: 1rem;
            width: 100%;
            max-width: 400px;
            margin: auto;
            margin-top: 100px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="forgot-password-box">', unsafe_allow_html=True)
    st.title("🔑 Forgot Password")

    username     = st.text_input("👨‍⚕️ Username", key="forgot_username").strip().lower()
    new_password = st.text_input("🔒 New Password", type="password", key="forgot_newpw")
    confirm_pw   = st.text_input("🔐 Confirm New Password", type="password", key="forgot_confirm")

    if st.button("Reset Password"):
        if not username or not new_password:
            st.error("❌ All fields are required.")
        else:
            row = load_user(username)
            if row is None:
                st.error("❌ Username not found.")
            elif new_password != confirm_pw:
                st.error("❌ Passwords do not match.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                update_password(username, hashed_pw)
                st.success("🎉 Password has been reset successfully! Please login with your new password.")

    st.markdown('</div>', unsafe_allow_html=True)

# Always call the page (app.py will import it conditionally)
forgot_password_page()
