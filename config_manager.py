import yaml
import bcrypt
import os

CONFIG_FILE = "config.yaml"

def load_users():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file) or {}
    return config.get("credentials", {}).get("usernames", {})

def add_user(username, name, plain_password):
    hashed_pw = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    # Load existing config or create new
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file) or {}
    else:
        config = {}

    # Ensure keys exist
    config.setdefault("credentials", {}).setdefault("usernames", {})

    # Prevent overwriting existing users
    if username in config["credentials"]["usernames"]:
        raise ValueError(f"Username '{username}' already exists!")

    # Add new user
    config["credentials"]["usernames"][username] = {
        "name": name,
        "password": hashed_pw
    }

    # Write back to config.yaml
    with open(CONFIG_FILE, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    print(f"✅ User '{username}' added successfully.")

# Example usage
if __name__ == "__main__":
    add_user("drsmith", "Dr. Smith", "heartsecure123")
