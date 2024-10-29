from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit

class PrivateChatWindow(QWidget):
    def __init__(self, username, target_users, peer_network):
        super().__init__()
        self.username = username
        self.target_users = target_users  # lista degli utenti destinatari
        self.peer_network = peer_network
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        if len(self.target_users) == 1:
            chat_with = self.target_users[0]
            self.setWindowTitle(f"Private Chat with {chat_with}")
        else:
            chat_with = ", ".join(self.target_users)
            self.setWindowTitle(f"Group Chat with {chat_with}")

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
            for target_username in self.target_users:
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    private_message = f"PRIVATE_MESSAGE|{self.username}|{message}"
                    self.peer_network.send_message(ip, 5001, private_message)
            self.input_message.clear()

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
