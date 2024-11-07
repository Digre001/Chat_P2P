from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import requests
BASE_URL = 'http://172.20.10.5:5003'  # Assicurati che sia l'indirizzo corretto della tua API

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
            print(f"Private key fetched successfully for {username}.")
            return serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
    print(f"Failed to fetch private key for {username}: {response.json().get('message', 'Unknown error')}")
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
        self.input_message.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def load_previous_messages(self):
        for target_user in self.target_users:
            messages = load_messages_from_db(self.username, target_user)
            for sender, message, timestamp in messages:  # Usa 'message' invece di 'encrypted_message'
                if sender == self.username:
                    display_message = message  # Messaggio già in chiaro
                else:
                    display_message = message  # Messaggio già in chiaro
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

    def receive_message(self, message):
        """Handles receiving a message from the peer network."""
        # Split the message to extract sender and content
        try:
            print(f"Received message pls pls pls: {message}")
            sender, encrypted_message_hex = message.split(': ', 1)  # Split on ': ' and take the rest as encrypted_message_hex
            
            # Assuming you have some logic to determine the message type
            message_type = "PRIVATE_MESSAGE"  # Or set based on your application logic
            
            # Convert the hex message back to bytes
            encrypted_message = bytes.fromhex(encrypted_message_hex.strip())  # Clean up any extra whitespace

            # Get the private key to decrypt the message
            private_key = get_private_key(self.username)

            try:
                # Decrypt the message
                decrypted_message = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode('utf-8')
                display_message = decrypted_message
            except Exception as e:
                print(f"Decryption failed: {e}")
                display_message = "[Failed to decrypt message]"

            # Append the received message to the chat window
            self.received_messages.append(f"{sender}: {display_message}")
            
        except ValueError:
            print("Received an invalid message format")


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
        self.input_message.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.input_message.text()
        if message:
            # Mostra il messaggio nella chat
            self.received_messages.append(f"{self.username}: {message}")
            for target_username in self.group_users:
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    group_message = f"GROUP_MESSAGE|{self.username}|{message}"
                    self.peer_network.send_message(ip, 5001, group_message)
            self.input_message.clear()

    def receive_message(self, message):
        self.received_messages.append(message)
