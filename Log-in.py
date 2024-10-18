import sys
import json
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

USER_DATA = 'users_data.json'

# Classe per la gestione degli utenti (logica di autenticazione)
class UserManager:
    def __init__(self, user_data_file=USER_DATA):
        self.user_data_file = user_data_file

    # Metodo per caricare i dati degli utenti
    def load_users(self):
        try:
            with open(self.user_data_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    # Metodo per salvare i dati degli utenti
    def save_users(self, users):
        with open(self.user_data_file, 'w') as file:
            json.dump(users, file, indent=4) #indent è usato per la leggibilità del file json

    # Metodo per registrare un nuovo utente
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

            users[username] = {
                'password': password_hash,
                'private_key': private_key_bytes.decode(),
                'public_key': public_key.decode()
            }
            self.save_users(users)
            return True, f"Registrazione completata per {username}"

    # Metodo per effettuare il login
    def login_user(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "Utente non trovato!"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != users[username]['password']:
            return False, "Password errata!"
        return True, f"Accesso effettuato per {username}!"

# Classe per l'interfaccia grafica (GUI)
class LoginApp(QWidget):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager  # Passiamo l'istanza di UserManager alla GUI
        self.init_ui()

    def init_ui(self):
        # Layout principale
        layout = QVBoxLayout()

        # Label e campo per il nome utente
        self.label_username = QLabel("Username:")
        layout.addWidget(self.label_username)
        self.entry_username = QLineEdit()
        layout.addWidget(self.entry_username)

        # Label e campo per la password
        self.label_password = QLabel("Password:")
        layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.entry_password)

        # Aggiungi uno spazio vuoto tra password e pulsanti
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Bottone di registrazione
        self.btn_register = QPushButton("Registrati")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register)

        # Bottone di login
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.login_user)
        layout.addWidget(self.btn_login)

        # Imposta il layout
        self.setLayout(layout)
        self.setWindowTitle("Login System")

    # Metodo per la registrazione di un utente
    def register_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()
        success, msg = self.user_manager.register_user(username, password)
        QMessageBox.information(self, "Registrazione", msg)

    # Metodo per il login di un utente
    def login_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()
        success, msg = self.user_manager.login_user(username, password)
        if success:
            QMessageBox.information(self, "Login", msg)
        else:
            QMessageBox.warning(self, "Errore", msg)

# Avvio dell'applicazione
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Inizializza il gestore degli utenti
    user_manager = UserManager()

    # Crea e mostra la finestra di login
    window = LoginApp(user_manager)
    window.show()

    # Avvia il loop dell'applicazione
    sys.exit(app.exec_())
