import streamlit as st
import yaml
import bcrypt

# Load user data from config.yaml
def load_users():
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        return config.get("credentials", {}).get("usernames", {})
    except FileNotFoundError:
        return {}

# Save user data to config.yaml
def save_user(username, hashed_password, name):
    users = load_users()

    # Add the new user to the 'users' dictionary
    users[username] = {"name": name, "password": hashed_password}

    # Save the updated users dictionary to config.yaml
    with open("config.yaml", "w") as file:
        yaml.dump({"credentials": {"usernames": users}}, file)

# Sign Up Page
def signup_page():
    st.markdown("""
        <style>
        .signup-box {
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

    # Image above the sign-up box
    st.image("Heart.png", width=120)

    # Sign-up form container
    st.markdown('<div class="signup-box">', unsafe_allow_html=True)

    st.title("🩺 Sign Up")
    username = st.text_input("👨‍⚕️ Username")
    name = st.text_input("📝 Full Name")
    password = st.text_input("🔒 Password", type="password")
    confirm_password = st.text_input("🔐 Confirm Password", type="password")

    if st.button("Sign Up"):
        if password == confirm_password:
            # Hash the password
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # Save new user
            save_user(username, hashed_pw, name)
            st.success("🎉 Sign up successful! Please login.")
        else:
            st.error("❌ Passwords do not match.")

    st.markdown('</div>', unsafe_allow_html=True)

# Run Sign Up page
signup_page()
