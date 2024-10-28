import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

USER_DATA = '../user_data.json'

class UserManager:
    def __init__(self, user_data_file=USER_DATA):
        self.user_data_file = user_data_file
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

    def register_user(self, username, password):
        if username in self.users:
            return False, "Username già in uso"

        # Hash della password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Generazione delle chiavi RSA usando cryptography
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

        # Salvataggio dei dati utente
        self.users[username] = {
            'password': password_hash,
            'private_key': private_key_bytes.decode(),
            'public_key': public_key.decode(),
        }
        self.save_users()
        return True, f"Registrazione completata per {username}"

    def login_user(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if username not in self.users or password_hash != self.users[username]['password']:
            return False, "Username o password errati"

        # Aggiornamento stato utente
        self.users[username]['status'] = 'online'
        self.save_users()
        return True, f"Accesso effettuato per {username}!"

    def logout_user(self, username):
        if username in self.users:
            return True, f"Logout effettuato per {username}"
        return False, "Utente inesistente"

    def get_connected_users(self):
        return {user: info for user, info in self.users.items() if info['status'] == 'online'}
