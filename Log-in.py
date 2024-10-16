import os
import json
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


# Percosrso del file json contenente i dati degli utenti
USER_DATA = 'user_data.json'

# Funzione per caricare i dati degli utenti
def load_users():
    if os.path.exists(USER_DATA):
        with open(USER_DATA, 'r') as file:
            return json.load(file)
    return {}

# Funzione per salvare i dati degli utenti (devo decidere se salvarli in un file json o due uno per i dati e uno per le password)
def save_users(users):
    with open(USER_DATA, 'w') as file:
        json.dump(users, file)

# Funzione per registrare un nuovo utente
def register_users(username, password):
    users = load_users()
    if username in users:
        print("Username già in uso")
        return False
    else:
        # Hash della password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Generazione della coppia di chiavi pubblica/privata
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

        # Salvataggio dei dati dell'utente
        users[username] = {
            'password': password_hash,
            'private_key': private_key_bytes.decode(),
            'public_key': public_key.decode()
        }
        save_users(users)
        print(f"Registrazione completata per l'utente {username}")
        return True

# Funzione per effettuare il login
def login_user(username, password):
    users = load_users()
    if username not in users:
        print("Utente non trovato!")
        return None
    user_data = users[username]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user_data['password_hash']:
        print("Password errata!")
        return None

    print(f"Login effettuato per {username}")
    return True