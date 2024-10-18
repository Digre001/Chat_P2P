import json
import hashlib

USER_DATA = 'users_data.json'

class UserManager:
    def __init__(self):
        self.user_data_file = USER_DATA
        self.load_users()

    def load_users(self):
        try:
            with open(self.user_data_file, 'r') as file:
                self.users = json.load(file)
        except FileNotFoundError:
            self.users = {}

    def save_users(self):
        with open(self.user_data_file, 'w') as file:
            json.dump(self.users, file, indent=4)

    def login_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if username not in self.users or password_hash != self.users[username]['password']:
            return False, "Incorrect username or password"
        
        return True, f"Logged in as {username}!"

    def get_connected_users(self):
        return {user: info for user, info in self.users.items() if info['status'] == 'online'}

# Example usage
if __name__ == "__main__":
    user_manager = UserManager()
    print(user_manager.get_connected_users())  # For testing purposes