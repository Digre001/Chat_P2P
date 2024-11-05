from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import sqlite3
import base64 

# Function to retrieve the public key of a specific user from the database
def get_public_key(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT public_key FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:  # Check if the key exists
        # Load the public key from a PEM-formatted string
        return serialization.load_pem_public_key(result[0].encode('utf-8'))
    return None

# Function to retrieve the private key of a specific user from the database
def get_private_key(username):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT private_key FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:  # Check if the key exists
        # Load the private key from a PEM-formatted string
        return serialization.load_pem_private_key(result[0].encode('utf-8'), password=None)
    return None

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
                    # Already plain text for sent messages
                    display_message = encrypted_message
                else:
                    # Decrypt the received message
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
                public_key = get_public_key(target_username)
                if public_key:
                    # Cripta il messaggio con la chiave pubblica del destinatario
                    encrypted_message = public_key.encrypt(
                        message.encode('utf-8'),
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )

                    # Codifica il messaggio cifrato in Base64 per la memorizzazione e la trasmissione
                    encrypted_message_base64 = base64.b64encode(encrypted_message).decode('utf-8')

                    # Salva il messaggio cifrato nel database
                    save_message_to_db(self.username, target_username, encrypted_message_base64)

                    # Invia il messaggio cifrato sulla rete
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        private_message = f"PRIVATE_MESSAGE|{self.username}|{encrypted_message_base64}"
                        self.peer_network.send_message(ip, 5001, private_message)

            # Visualizza il messaggio inviato nell'interfaccia
            self.received_messages.append(f"{self.username}: {message}")
            self.input_message.clear()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def receive_message(self, full_message):
        # Divide il messaggio in parti separate
        parts = full_message.split('|')
        
        # Verifica che il formato sia corretto (almeno tre parti)
        if len(parts) < 3:
            self.received_messages.append("[Invalid message format]")
            return
        
        # Estrai il mittente e il messaggio cifrato in Base64
        sender = parts[1]
        message_base64 = parts[2]

        # Decodifica da Base64 a bytes
        try:
            encrypted_message = base64.b64decode(message_base64)
        except ValueError:
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
        except Exception:
            self.received_messages.append("[Failed to decrypt message]")

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
            self.received_messages.append(f"{self.username}: {message}")
            for target_username in self.group_users:
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    group_message = f"GROUP_MESSAGE|{self.username}|{message}"
                    self.peer_network.send_message(ip, 5001, group_message)
            self.input_message.clear()

    def receive_message(self, message):
        self.received_messages.append(message)





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