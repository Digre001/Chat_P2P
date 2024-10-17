from PyQt5.QtWidgets import QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
import socket
import threading
import time
import logging

class ChatWindow(QMainWindow):
    def __init__(self, username, user_manager):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.init_ui()

        # Imposta lo stato dell'utente a "attivo"
        self.user_manager.update_user_status(username, 'active')

        # Configura il logging
        self.setup_logging()

        # Avvia il thread per controllare gli utenti attivi
        threading.Thread(target=self.monitor_users, daemon=True).start()

    def init_ui(self):
        self.setWindowTitle("Chat")
        self.setGeometry(100, 100, 400, 300)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)

        self.message_input = QLineEdit(self)

        self.send_button = QPushButton("Invia", self)
        self.send_button.clicked.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.chat_display)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Avvia il thread per ricevere messaggi
        threading.Thread(target=self.start_receiving, daemon=True).start()

    def setup_logging(self):
        logging.basicConfig(filename='../active_users.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    def closeEvent(self, event):
        # Aggiorna lo stato dell'utente a "inattivo" prima di chiudere
        self.user_manager.update_user_status(self.username, 'inactive')
        event.accept()  # Chiude la finestra

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.broadcast_message(message)
            self.message_input.clear()

    def broadcast_message(self, message):
        active_users = self.user_manager.get_active_users()
        for user, data in active_users.items():
            if user != self.username:
                try:
                    # Invia il messaggio usando il socket UDP
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(f"{self.username}: {message}".encode(), (data['ip'], data['port']))
                except Exception as e:
                    print(f"Errore nell'invio a {user}: {e}")

    def start_receiving(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', self.user_manager.load_users()[self.username]['port']))  # Bind sulla porta assegnata

        while True:
            try:
                message, addr = sock.recvfrom(1024)
                self.chat_display.append(message.decode())
            except Exception as e:
                print(f"Errore nella ricezione: {e}")

    def monitor_users(self):
        while True:
            time.sleep(2)  # Aspetta 2 secondi
            active_users = self.user_manager.get_active_users()

            # Registra solo gli utenti attivi che non sono l'utente corrente
            for user in active_users.keys():
                if user != self.username:
                    logging.info(f"Utenti attivi: {user}")
