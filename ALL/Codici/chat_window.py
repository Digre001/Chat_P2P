from PyQt5.QtWidgets import QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
import socket
import threading
import time
import logging
import os



class ChatWindow(QMainWindow):
    def __init__(self, username, user_manager):
        super().__init__()
        self.username = username
        self.user_manager = user_manager
        self.init_ui()

        self.user_manager.update_user_status(username, 'active')
        self.setup_logging()

        # Avvia il thread per monitorare gli utenti attivi
        threading.Thread(target=self.monitor_users, daemon=True).start()

        # Avvia il thread per aggiornare l'etichetta con gli utenti attivi
        threading.Thread(target=self.update_active_users_label, daemon=True).start()

    def init_ui(self):
        self.setWindowTitle(f"Chat - {self.username}")
        self.setGeometry(100, 100, 500, 400)

        # Etichetta per mostrare il nome dell'utente
        self.label_user = QLabel(f"Utente: {self.username}", self)

        # Display della chat
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #f0f0f0; color: black;")

        # Campo per inserire il messaggio
        self.message_input = QLineEdit(self)
        self.message_input.returnPressed.connect(self.send_message)  # Connetti "Invio" all'invio del messaggio
        self.message_input.setPlaceholderText("Scrivi il tuo messaggio qui...")

        # Pulsante di invio
        self.send_button = QPushButton("Invia", self)
        self.send_button.clicked.connect(self.send_message)

        # Etichetta per mostrare gli utenti attivi
        self.active_users_label = QLabel("Utenti attivi: Nessuno", self)

        # Layout principale
        layout = QVBoxLayout()
        layout.addWidget(self.label_user)  # Nome utente
        layout.addWidget(self.chat_display)  # Display della chat
        layout.addWidget(self.message_input)  # Input messaggio
        layout.addWidget(self.send_button)  # Pulsante invia
        layout.addWidget(self.active_users_label)  # Etichetta utenti attivi

        # Contenitore per il layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Avvia il thread per ricevere messaggi
        threading.Thread(target=self.start_receiving, daemon=True).start()

    def setup_logging(self):
        # Modifica il percorso del file di log per puntare alla cartella Dati
        log_file = os.path.join('Dati', 'active_users.log')
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

    def closeEvent(self, event):
        # Aggiorna lo stato dell'utente a "inattivo" prima di chiudere
        self.user_manager.update_user_status(self.username, 'inactive')
        event.accept()  # Chiude la finestra

    def send_message(self):
        message = self.message_input.text()
        if message:
            # Mostra il messaggio anche nella propria finestra
            self.display_message(self.username, message)  # Mostra il messaggio inviato
            self.broadcast_message(message)
            self.message_input.clear()

    def display_message(self, user, message):
        """Mostra un messaggio nel display della chat."""
        self.chat_display.append(f"<b>{user}:</b> {message}")

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
        users = self.user_manager.load_users()
        if self.username not in users:
            print(f"Errore: utente {self.username} non trovato per ricezione messaggi.")  # Debug
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', users[self.username]['port']))  # Bind sulla porta assegnata

        while True:
            try:
                message, addr = sock.recvfrom(1024)
                # Mostra i messaggi ricevuti
                self.display_message(*message.decode().split(': ', 1))  # Mostra il messaggio con il nome utente
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

    def update_active_users_label(self):
        """Funzione per aggiornare l'etichetta degli utenti attivi nella GUI."""
        while True:
            time.sleep(2)  # Aggiorna ogni 2 secondi
            active_users = self.user_manager.get_active_users()

            # Ottieni la lista degli utenti attivi, escludendo l'utente corrente
            active_users_list = ', '.join([user for user in active_users.keys() if user != self.username])
            if not active_users_list:
                active_users_list = "Nessuno"

            # Aggiorna l'etichetta nella GUI in modo thread-safe
            self.active_users_label.setText(f"Utenti attivi: {active_users_list}")
