from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal
import sqlite3

class PrivateChatWindow(QWidget):

    closed_signal = pyqtSignal()

    def __init__(self, username, target_users, peer_network):
        super().__init__()
        self.username = username
        self.target_users = target_users  # lista degli utenti destinatari
        self.peer_network = peer_network
        self.init_ui()

        # Carica i messaggi passati
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
            for sender, message, timestamp in messages:
                self.received_messages.append(f"{sender} ({timestamp}): {message}")

    def send_message(self):
        message = self.input_message.text()
        if message:
            for target_username in self.target_users:
                # Load recipient's public key
                public_key_str, _ = load_user_keys(target_username)
                if public_key_str:
                    # Load public key
                    public_key = serialization.load_pem_public_key(public_key_str.encode())

                    # Encrypt the message
                    encrypted_message = public_key.encrypt(
                        message.encode(),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    # Send the encrypted message
                    private_message = f"PRIVATE_MESSAGE|{self.username}|{encrypted_message.hex()}"
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        self.peer_network.send_message(ip, 5001, private_message)
                        # Save the message to the database
                        save_message_to_db(self.username, target_username, message)

            self.input_message.clear()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def receive_message(self, message):
        if message.startswith("PRIVATE_MESSAGE|"):
            _, sender_username, encrypted_content = message.split("|", 2)
            # Load this user's private key
            _, private_key_str = load_user_keys(self.username)
            if private_key_str:
                # Load private key
                private_key = serialization.load_pem_private_key(private_key_str.encode(), password=None)

                # Decrypt the message
                encrypted_message = bytes.fromhex(encrypted_content)
                decrypted_message = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()

                self.received_messages.append(f"{sender_username}: {decrypted_message}")


class GroupChatWindow(QWidget):
    def __init__(self, username, group_users, peer_network):
        super().__init__()
        self.username = username
        self.group_users = group_users  # lista degli utenti del gruppo
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
            for target_username in self.target_users:
                # Load recipient's public key
                public_key_str, _ = load_user_keys(target_username)
                if public_key_str:
                    # Load public key
                    public_key = serialization.load_pem_public_key(public_key_str.encode())

                    # Encrypt the message
                    encrypted_message = public_key.encrypt(
                        message.encode(),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    # Send the encrypted message
                    private_message = f"PRIVATE_MESSAGE|{self.username}|{encrypted_message.hex()}"
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        self.peer_network.send_message(ip, 5001, private_message)
                        # Save the message to the database
                        save_message_to_db(self.username, target_username, message)

            self.input_message.clear()

    def receive_message(self, message):
        if message.startswith("PRIVATE_MESSAGE|"):
            _, sender_username, encrypted_content = message.split("|", 2)
            # Load this user's private key
            _, private_key_str = load_user_keys(self.username)
            if private_key_str:
                # Load private key
                private_key = serialization.load_pem_private_key(private_key_str.encode(), password=None)

                # Decrypt the message
                encrypted_message = bytes.fromhex(encrypted_content)
                decrypted_message = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode()

                self.received_messages.append(f"{sender_username}: {decrypted_message}")





#####    DATABASE    #####     PER SALVARE I MESSAGGI      #####


def initialize_database():
    """Creates the private_chats table if it doesn't exist."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Funzione per salvare un messaggio nel database
def save_message_to_db(sender, receiver, message):
    initialize_database()
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT INTO private_chats (sender, receiver, message) 
        VALUES (?, ?, ?)
    ''', (sender, receiver, message))
    conn.commit()
    conn.close()

# Funzione per caricare i messaggi passati dal database
def load_messages_from_db(user1, user2):
    initialize_database()
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, message, timestamp FROM private_chats
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp
    ''', (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    return messages

# Funzione per caricare le chiavi RSA dell'utente dal database
def load_user_keys(username):
    """Loads the RSA public and private keys for the specified user from the database."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT public_key, private_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1]  # Return public_key, private_key
    return None, None  # If user not found