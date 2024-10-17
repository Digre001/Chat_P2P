import json
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

USER_DATA = '/Users/paya/Desktop/Chat_p2p/Prova_GUI_avanzata/user_data.json'

class UserManager:
    def __init__(self, user_data_file=USER_DATA):
        self.user_data_file = user_data_file

    def load_users(self):
        try:
            with open(self.user_data_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_users(self, users):
        with open(self.user_data_file, 'w') as file:
            json.dump(users, file, indent=4)

    def register_user(self, username, password):
        users = self.load_users()
        if username in users:
            return False, "Username già in uso"
        else:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
            )
            public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Genera una porta casuale tra 2000 e 3000
            port = self.find_available_port(users)

            users[username] = {
                'password': password_hash,
                'private_key': private_key_bytes.decode(),
                'public_key': public_key.decode(),
                'status': 'inactive',  # Lo stato è inattivo dopo la registrazione
                'ip': 'localhost',
                'port': port
            }
            self.save_users(users)
            return True, f"Registrazione completata per {username}, porta assegnata: {port}"

    def find_available_port(self, users):
        assigned_ports = {data['port'] for data in users.values()}
        for port in range(2000, 3001):
            if port not in assigned_ports:
                return port
        raise RuntimeError("Nessuna porta disponibile nel range 2000-3000")

    def login_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "Utente non trovato!"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != users[username]['password']:
            return False, "Password errata!"
        users[username]['status'] = 'active'  # Cambia lo stato in attivo al login
        self.save_users(users)
        return True, f"Accesso effettuato per {username}!"

    def update_user_status(self, username, status):
        users = self.load_users()
        if username in users:
            users[username]['status'] = status
            self.save_users(users)

    def get_active_users(self):
        users = self.load_users()
        active_users = {user: data for user, data in users.items() if data.get('status') == 'active'}
        return active_users
