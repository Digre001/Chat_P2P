from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import sqlite3
import base64 
import requests
BASE_URL = 'http://192.168.110.42:5003'  # Assicurati che sia l'indirizzo corretto della tua API

# Function to retrieve the public key of a specific user from the database
def get_public_key(username):
    """Richiede la chiave pubblica di un utente tramite l'API."""
    response = requests.get(f"{BASE_URL}/get_public_key/{username}")
    if response.status_code == 200:
        public_key_pem = response.json().get("public_key")
        if public_key_pem:
            return serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
    return None

def get_private_key(username):
    """Richiede la chiave privata di un utente tramite l'API."""
    response = requests.get(f"{BASE_URL}/get_private_key/{username}")
    if response.status_code == 200:
        private_key_pem = response.json().get("private_key")
        if private_key_pem:
            return serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    return None


def initialize_database():
    """Effettua una richiesta all'API per inizializzare la tabella private_chats."""
    response = requests.post(f"{BASE_URL}/initialize_database")
    if response.status_code == 201:
        print("Database initialized successfully!")
    else:
        print("Failed to initialize database:", response.json().get("message", "Unknown error"))


def save_message_to_db(sender, receiver, message):
    """Invia un messaggio in chiaro all'API per salvarlo nel database."""
    data = {
        "sender": sender,
        "receiver": receiver,
        "message": message
    }
    response = requests.post(f"{BASE_URL}/save_message", json=data)
    return response.json()


def load_messages_from_db(user1, user2):
    """Carica i messaggi tra due utenti dal database tramite l'API."""
    params = {
        "user1": user1,
        "user2": user2
    }
    response = requests.get(f"{BASE_URL}/load_messages", params=params)
    if response.status_code == 200:
        return response.json()["messages"]
    else:
        return []


def load_user_keys(username):
    """Carica le chiavi RSA dell'utente tramite l'API."""
    response = requests.get(f"{BASE_URL}/get_keys/{username}")
    if response.status_code == 200:
        data = response.json()
        return data.get("public_key"), data.get("private_key")
    return None, None


# Example usage in your PrivateChatWindow class
class PrivateChatWindow(QWidget):

    closed_signal = pyqtSignal()

    def __init__(self, username, target_users, peer_network):
        super().__init__()
        self.username = username
        self.target_users = target_users  # list of target users
        self.peer_network = peer_network
        self.init_ui()

        # Load past messages
        self.load_previous_messages()

    def init_ui(self):
        layout = QVBoxLayout()
        chat_with = ", ".join(self.target_users)
        self.setWindowTitle(f"Private Chat with {chat_with}")

        self.received_messages = QTextEdit()
        self.received_messages.setPlaceholderText("Receive messages here...")
        self.received_messages.setReadOnly(True)
        layout.addWidget(self.received_messages)

        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("Write a message...")
        layout.addWidget(self.input_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def load_previous_messages(self):
        for target_user in self.target_users:
            messages = load_messages_from_db(self.username, target_user)
            for sender, encrypted_message, timestamp in messages:
                if sender == self.username:
                    display_message = encrypted_message
                else:
                    private_key = get_private_key(self.username)
                    try:
                        decrypted_message = private_key.decrypt(
                            encrypted_message,
                            padding.OAEP(
                                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                algorithm=hashes.SHA256(),
                                label=None
                            )
                        ).decode('utf-8')
                        display_message = decrypted_message
                    except Exception:
                        display_message = "[Failed to decrypt message]"
                self.received_messages.append(f"{sender} ({timestamp}): {display_message}")

    def send_message(self):
        message = self.input_message.text()
        if message:
            for target_username in self.target_users:
                # Salva il messaggio in chiaro nel database
                save_message_to_db(self.username, target_username, message)

                public_key = get_public_key(target_username)
                if public_key:
                    # Cifra il messaggio con la chiave pubblica del destinatario
                    encrypted_message = public_key.encrypt(
                        message.encode('utf-8'),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )

                    # Converti il messaggio cifrato in formato esadecimale per JSON
                    encrypted_message_hex = encrypted_message.hex()

                    # Invia il messaggio cifrato
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        private_message = f"PRIVATE_MESSAGE|{self.username}|{encrypted_message_hex}"
                        self.peer_network.send_message(ip, 5001, private_message)

            # Mostra il messaggio inviato nella finestra di chat
            self.received_messages.append(f"{self.username}: {message}")
            self.input_message.clear()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def receive_message(self, full_message):
        # Divide il messaggio in parti separandolo da '|'
        parts = full_message.split('|')

        # Verifica che il formato sia corretto: deve avere esattamente tre parti
        if len(parts) != 3 or parts[0] != "PRIVATE_MESSAGE":
            self.received_messages.append("[Invalid message format]")
            return

        # Estrai il mittente e il messaggio cifrato in formato esadecimale
        sender = parts[1]
        message_hex = parts[2]

        # Converti da esadecimale a bytes
        try:
            encrypted_message = bytes.fromhex(message_hex)
        except ValueError:
            # Messaggio non valido; logga o notifica l'errore
            self.received_messages.append("[Invalid message format]")
            return

        # Decripta il messaggio
        private_key = get_private_key(self.username)

        try:
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode('utf-8')

            # Mostra il messaggio decifrato con il mittente
            self.received_messages.append(f"{sender}: {decrypted_message}")
        except Exception as e:
            self.received_messages.append("[Failed to decrypt message]")
            print(f"Error decrypting message: {e}")

class GroupChatWindow(QWidget):
    def __init__(self, username, group_users, peer_network):
        super().__init__()
        self.username = username
        self.group_users = group_users
        self.peer_network = peer_network
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        group_title = ", ".join(self.group_users)
        self.setWindowTitle(f"Group Chat with {group_title}")

        self.received_messages = QTextEdit()
        self.received_messages.setPlaceholderText("Receive messages here...")
        self.received_messages.setReadOnly(True)
        layout.addWidget(self.received_messages)

        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("Write a message...")
        layout.addWidget(self.input_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.input_message.text()
        if message:
            self.received_messages.append(f"{self.username}: {message}")
            for target_username in self.group_users:
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    group_message = f"GROUP_MESSAGE|{self.username}|{message}"
                    self.peer_network.send_message(ip, 5001, group_message)
            self.input_message.clear()

    def receive_message(self, message):
        self.received_messages.append(message)

