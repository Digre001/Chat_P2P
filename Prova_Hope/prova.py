import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit, QMessageBox
from user_manager import UserManager
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from udp_discovery import PeerNetwork  # Assuming PeerNetwork is in peer_network.py

# Worker class for receiving messages asynchronously
class MessageReceiver(QThread):
    message_received = pyqtSignal(str)  # Signal emitted when a message is received

    def __init__(self, peer_network, parent=None):
        super().__init__(parent)
        self.peer_network = peer_network

    def run(self):
        # Start the peer network TCP server to listen for messages
        self.peer_network.start_peer_server(5001)  # Assuming peers communicate on port 5001

# Login Window Class
class LoginApp(QWidget):
    def __init__(self, user_manager, peer_network):
        super().__init__()
        self.user_manager = user_manager
        self.peer_network = peer_network
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Username")
        layout.addWidget(self.username_field)

        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_field)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        self.setWindowTitle("Login")

    def login_user(self):
        username = self.username_field.text()
        password = self.password_field.text()
        success, msg = self.user_manager.login_user(username, password)

        if success:
            self.peer_network.start(username)  # Pass the username to start the network
            self.open_message_app(username)
        else:
            QMessageBox.warning(self, "Error", msg)

    def open_message_app(self, username):
        self.message_app = MessageApp(username, self.user_manager, self.peer_network)
        self.message_app.show()
        self.close()

# Finestra principale per i messaggi
class MessageApp(QWidget):
    def __init__(self, username, user_manager, peer_network):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.peer_network = peer_network
        self.private_chats = {}  # Dizionario per memorizzare le finestre di chat private/gruppo
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
            # Controlla se il messaggio è un comando per un utente specifico o un gruppo
            direct_message_match = re.match(r'^!(\w+)', message)
            group_message_match = re.match(r'^!!\(([\w, ]+)\)', message)

            if direct_message_match:
                # Chat privata con un singolo utente
                target_username = direct_message_match.group(1)
                self.open_private_chat(target_username)
            elif group_message_match:
                # Chat di gruppo
                target_usernames = [name.strip() for name in group_message_match.group(1).split(',')]
                self.open_group_chat(target_usernames)
            else:
                # Se non è specificato alcun comando, invia il messaggio a tutti i peer
                self.received_messages.append(f"{self.username}: {message}")
                connected_users = self.peer_network.get_connected_ips()  # Dizionario di IP collegati e nomi utenti
                for ip, _ in connected_users.items():
                    self.peer_network.send_message(ip, 5001, f"{self.username}: {message}")
        
            self.input_message.clear()

    def receive_message(self, message):
        """Riceve i messaggi e li mostra nella finestra principale."""
        self.received_messages.append(f"{message}")

    def open_private_chat(self, target_username):
        """Apre una finestra di chat privata con un utente."""
        if target_username not in self.private_chats:
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
        if group_key not in self.private_chats:
            # Se la chat di gruppo non è già aperta, aprila
            group_chat = PrivateChatWindow(self.username, target_usernames, self.peer_network)
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

# Finestra principale per i messaggi
class MessageApp(QWidget):
    def __init__(self, username, user_manager, peer_network):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.peer_network = peer_network
        self.private_chats = {}  # Dizionario per memorizzare le finestre di chat private/gruppo
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
            group_message_match = re.match(r'^!gruppo\s+([\w,]+)', message)
            
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
                self.received_messages.append(f"{self.username}: {message}")
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
            # Messaggio di gruppo
            _, sender_username, msg_content = message.split("|", 2)
            for group_chat in self.group_chats.values():
                if sender_username in group_chat.group_users:
                    group_chat.receive_message(f"{sender_username}: {msg_content}")
                    break
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
        if target_username not in self.private_chats:
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
        if group_key not in self.private_chats:
            # Se la chat di gruppo non è già aperta, aprila
            group_chat = PrivateChatWindow(self.username, target_usernames, self.peer_network)
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


# Starting the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_manager = UserManager()
    peer_network = PeerNetwork()  # Initialize peer network
    login_window = LoginApp(user_manager, peer_network)
    login_window.show()
    sys.exit(app.exec_())
