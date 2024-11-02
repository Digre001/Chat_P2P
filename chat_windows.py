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
            # Salva il messaggio nel database
            for target_username in self.target_users:
                save_message_to_db(self.username, target_username, message)

            #invia il messaggio
            self.received_messages.append(f"{self.username}: {message}")
            for target_username in self.target_users:
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    private_message = f"PRIVATE_MESSAGE|{self.username}|{message}"
                    self.peer_network.send_message(ip, 5001, private_message)
            self.input_message.clear()

    def closeEvent(self, event):
        self.closed_signal.emit()
        event.accept()

    def receive_message(self, message):
        self.received_messages.append(message)


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