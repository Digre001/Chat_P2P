import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from chat_windows import PrivateChatWindow, GroupChatWindow


class MessageApp(QWidget):
    def __init__(self, username, user_manager, peer_network):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.peer_network = peer_network
        self.private_chats = {}  # Dizionario per memorizzare le finestre di chat private/gruppo
        self.group_chats = {}  # Dizionario per memorizzare le finestre di chat di gruppo
        self.init_ui()

        # Configura il ricevitore di messaggi
        self.message_receiver = MessageReceiver(peer_network)
        self.message_receiver.message_received.connect(self.receive_message)
        self.message_receiver.start()

        # Connetti il segnale del peer network per ricevere i messaggi
        self.peer_network.message_received_signal.connect(self.receive_message)

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_user = QLabel(f"Welcome, {self.username}!")
        layout.addWidget(self.label_user)

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

        self.connected_users_label = QLabel("Connected Devices:")
        layout.addWidget(self.connected_users_label)

        self.connected_users_display = QTextEdit()
        self.connected_users_display.setReadOnly(True)
        layout.addWidget(self.connected_users_display)

        self.setLayout(layout)
        self.setWindowTitle("Messages")

        self.update_connected_users()

        # Timer per aggiornare la lista degli utenti collegati
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_connected_users)
        self.timer.start(1000)  # Aggiorna ogni secondo

    def send_message(self):
        message = self.input_message.text()
        if message:
            # Comando per la chat privata (es. `!utente`)
            direct_message_match = re.match(r'^!(\w+)', message)
            # Comando per la chat di gruppo (es. `!gruppo utente1,utente2`)
            group_message_match = re.match(r'^!!\s+([\w,]+)', message)

            if direct_message_match:
                # Chat privata con un singolo utente
                target_username = direct_message_match.group(1)
                self.open_private_chat(target_username)
                ip = self.peer_network.get_ip_by_username(target_username)
                if ip:
                    private_message = f"PRIVATE_CHAT_REQUEST|{self.username}"
                    self.peer_network.send_message(ip, 5001, private_message)

            elif group_message_match:
                # Chat di gruppo con più utenti
                target_users = group_message_match.group(1).split(",")
                self.open_group_chat(target_users)
                for target_username in target_users:
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        group_request = f"GROUP_CHAT_REQUEST|{self.username}|{','.join(target_users)}"
                        self.peer_network.send_message(ip, 5001, group_request)

            else:
                # Messaggio pubblico
                for ip, _ in self.peer_network.get_connected_ips().items():
                    self.peer_network.send_message(ip, 5001, f"{self.username}: {message}")

            self.input_message.clear()

    def receive_message(self, message):
        if message.startswith("PRIVATE_CHAT_REQUEST|"):
            requester_username = message.split("|")[1]
            self.open_private_chat(requester_username)
        elif message.startswith("GROUP_CHAT_REQUEST|"):
            _, requester_username, group_usernames = message.split("|", 2)
            group_users = group_usernames.split(",")
            if requester_username not in group_users:
                group_users.append(requester_username)
            self.open_group_chat(group_users)
        elif message.startswith("GROUP_MESSAGE|"):
            _, sender_username, msg_content = message.split("|", 2)
            for group_chat in self.group_chats.values():
                if sender_username in group_chat.group_users:
                    # Invia il messaggio a tutti gli utenti del gruppo
                    for user in group_chat.group_users:
                        if user in self.private_chats:  # Assicurati che l'utente abbia una chat privata aperta
                            self.private_chats[user].receive_message(f"{sender_username}: {msg_content}")
        elif message.startswith("PRIVATE_MESSAGE|"):
            _, sender_username, msg_content = message.split("|", 2)
            if sender_username in self.private_chats:
                self.private_chats[sender_username].receive_message(f"{sender_username}: {msg_content}")
            else:
                self.open_private_chat(sender_username)
                self.private_chats[sender_username].receive_message(f"{sender_username}: {msg_content}")
        else:
            self.received_messages.append(message)

    def open_private_chat(self, target_username):
        """Apre una finestra di chat privata con un utente."""
        if target_username not in self.private_chats or not self.private_chats[target_username].isVisible():
            # Se la chat privata non è già aperta, aprila
            private_chat = PrivateChatWindow(self.username, [target_username], self.peer_network)
            private_chat.show()
            self.private_chats[target_username] = private_chat
        else:
            # Porta la finestra esistente in primo piano
            self.private_chats[target_username].activateWindow()

    def open_group_chat(self, target_usernames):
        """Apre una finestra di chat di gruppo."""
        group_key = ",".join(sorted(target_usernames))
        if group_key not in self.private_chats or not self.private_chats[group_key].isVisible():
            # Se la chat di gruppo non è già aperta, aprila
            group_chat = GroupChatWindow(self.username, target_usernames, self.peer_network)
            group_chat.show()
            self.private_chats[group_key] = group_chat
        else:
            # Porta la finestra esistente in primo piano
            self.private_chats[group_key].activateWindow()

    def update_connected_users(self):
        """Aggiorna la lista degli utenti collegati nella finestra principale."""
        connected_users_info = self.peer_network.get_connected_ips()
        user_list = "\n".join([f"{ip}: {username}" for ip, username in connected_users_info.items()])
        self.connected_users_display.setPlainText(user_list)

class MessageReceiver(QThread):
    message_received = pyqtSignal(str)  # Signal emitted when a message is received

    def __init__(self, peer_network, parent=None):
        super().__init__(parent)
        self.peer_network = peer_network

    def run(self):
        # Start the peer network TCP server to listen for messages
        self.peer_network.start_peer_server(5001)  # Assuming peers communicate on port 5001
