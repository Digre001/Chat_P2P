import requests

class UserManager:
    BASE_URL = 'http://192.168.178.220:5003'  # Adjust to your API server address

    def register_user(self, username, password):
        response = requests.post(f"{self.BASE_URL}/register", json={"username": username, "password": password})
        if response.status_code == 201:
            return True, response.json()["message"]
        return False, response.json()["message"]

    def login_user(self, username, password):
        response = requests.post(f"{self.BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            return True, response.json()["message"]
        return False, response.json()["message"]
