import re
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from chat_windows import PrivateChatWindow, GroupChatWindow


class MessageApp(QWidget):
    '''
    La classe MessageApp rappresenta un'applicazione di messaggistica in tempo reale basata su PyQt.

    Parametri:
        - username: Nome dell'utente corrente.
        - user_manager: Gestore per la gestione degli utenti.
        - peer_network: Rete peer-to-peer usata per inviare e ricevere messaggi tra utenti.

    Metodi:
        - __init__(self, username, user_manager, peer_network): Costruttore della classe che inizializza i parametri di istanza e configura l'interfaccia utente.
        - init_ui(self): Metodo che configura l'interfaccia utente principale dell'applicazione.
        - send_message(self): Invia un messaggio al destinatario specificato, supportando messaggi pubblici, privati e di gruppo.
        - receive_message(self, message): Gestisce la ricezione dei messaggi, includendo richieste di chat private e di gruppo.
        - open_private_chat(self, target_username): Apre una finestra di chat privata con un altro utente.
        - open_group_chat(self, target_usernames): Apre una finestra di chat di gruppo con una lista di utenti.
        - update_connected_users(self): Aggiorna la lista degli utenti collegati e li visualizza nell'interfaccia.
    '''

    def __init__(self, username, user_manager, peer_network):
        """Inizializza un'istanza di MessageApp, configurando i parametri di utente, rete, interfaccia e ricevitori di messaggi.

        Parametri:
            - username: Il nome dell'utente corrente.
            - user_manager: Oggetto per la gestione degli utenti.
            - peer_network: Oggetto che rappresenta la rete peer-to-peer per la comunicazione tra utenti.
        """
        super().__init__()
        self.username = username  # Nome utente dell'utente corrente
        self.user_manager = user_manager  # Gestore degli utenti collegati
        self.peer_network = peer_network  # Rete peer-to-peer per la comunicazione
        self.private_chats = {}  # Dizionario per memorizzare le finestre di chat private
        self.group_chats = {}  # Dizionario per memorizzare le finestre di chat di gruppo
        self.init_ui()  # Inizializza l'interfaccia utente

        # Configura il ricevitore di messaggi
        self.message_receiver = MessageReceiver(peer_network)  # Crea un ricevitore di messaggi
        self.message_receiver.message_received.connect(
            self.receive_message)  # Collega il segnale di ricezione dei messaggi alla funzione di ricezione
        self.message_receiver.start()  # Avvia il ricevitore di messaggi

        # Connetti il segnale del peer network per ricevere i messaggi
        self.peer_network.message_received_signal.connect(self.receive_message)

    def init_ui(self):
        """Configura l'interfaccia utente principale dell'applicazione, includendo campi per la visualizzazione dei messaggi e l'inserimento del testo."""
        layout = QVBoxLayout()  # Crea un layout verticale per l'interfaccia

        self.label_user = QLabel(f"Welcome, {self.username}!")  # Etichetta di benvenuto con il nome dell'utente
        layout.addWidget(self.label_user)

        self.received_messages = QTextEdit()  # Campo di testo per i messaggi ricevuti
        self.received_messages.setPlaceholderText("Receive messages here...")
        self.received_messages.setReadOnly(True)  # Imposta il campo come di sola lettura
        layout.addWidget(self.received_messages)

        self.input_message = QLineEdit()  # Campo per inserire i messaggi da inviare
        self.input_message.setPlaceholderText("Write a message...")
        layout.addWidget(self.input_message)
        self.input_message.returnPressed.connect(self.send_message)  # Invia il messaggio premendo Invio

        self.send_button = QPushButton("Send")  # Pulsante per inviare il messaggio
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.connected_users_label = QLabel("Connected Devices:")  # Etichetta per la lista degli utenti connessi
        layout.addWidget(self.connected_users_label)

        self.connected_users_display = QTextEdit()  # Campo di testo per visualizzare gli utenti connessi
        self.connected_users_display.setReadOnly(True)
        layout.addWidget(self.connected_users_display)

        # Istruzioni per l'avvio delle chat privata e di gruppo
        self.instructions_label = QLabel(
            "!’nome utente’ ------> avvia chat privata\n"
            "!! ‘nome utente’,’nome utente’ ----> avvia chat di gruppo con gli utenti\n"
            "(ricorda lo spazio per la chat di gruppo dai punti esclamativi)"
        )
        self.instructions_label.setStyleSheet(
            "background-color: lightgray; padding: 10px; border-radius: 5px;"
        )
        layout.addWidget(self.instructions_label)

        self.setLayout(layout)  # Imposta il layout dell'interfaccia
        self.setWindowTitle("Messages")  # Titolo della finestra

        self.update_connected_users()  # Aggiorna la lista degli utenti connessi

        # Timer per aggiornare la lista degli utenti collegati ogni secondo
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_connected_users)
        self.timer.start(1000)

    def send_message(self):
        """Invia un messaggio specificato, supportando chat pubbliche, private e di gruppo."""
        message = self.input_message.text()  # Ottiene il testo del messaggio
        if message:
            # Riconosce un comando di chat privata (es. `!utente`)
            direct_message_match = re.match(r'^!(\w+)', message)
            # Riconosce un comando di chat di gruppo (es. `!! utente1,utente2`)
            group_message_match = re.match(r'^!!\s+([\w,]+)', message)

            if direct_message_match:
                # Chat privata con un utente specifico
                target_username = direct_message_match.group(1)
                self.open_private_chat(target_username)  # Apre la chat privata
                ip = self.peer_network.get_ip_by_username(target_username)  # Ottiene l'IP del destinatario
                if ip:
                    private_message = f"PRIVATE_CHAT_REQUEST|{self.username}"  # Crea il messaggio di richiesta
                    self.peer_network.send_message(ip, 5001, private_message)  # Invia il messaggio

            elif group_message_match:
                # Chat di gruppo con più utenti
                target_users = group_message_match.group(1).split(",")
                self.open_group_chat(target_users)  # Apre la chat di gruppo
                for target_username in target_users:
                    ip = self.peer_network.get_ip_by_username(target_username)
                    if ip:
                        group_request = f"GROUP_CHAT_REQUEST|{self.username}|{','.join(target_users)}"
                        self.peer_network.send_message(ip, 5001, group_request)

            else:
                # Messaggio pubblico inviato a tutti gli utenti connessi
                for ip, _ in self.peer_network.get_connected_ips().items():
                    self.peer_network.send_message(ip, 5001, f"{self.username}: {message}")

            self.input_message.clear()  # Svuota il campo di input

    def receive_message(self, message):
        """Riceve e gestisce un messaggio in arrivo, creando o aggiornando le chat necessarie.

        Parametri:
            - message: Messaggio ricevuto che può includere richieste di chat privata, di gruppo o messaggi di testo.
        """
        if message.startswith("PRIVATE_CHAT_REQUEST|"):
            requester_username = message.split("|")[1]  # Nome utente del richiedente
            self.open_private_chat(requester_username)  # Apre la chat privata con il richiedente
        elif message.startswith("GROUP_CHAT_REQUEST|"):
            _, requester_username, group_usernames = message.split("|", 2)  # Estrae dettagli della chat
            group_users = group_usernames.split(",")
            if requester_username not in group_users:
                group_users.append(requester_username)
            self.open_group_chat(group_users)  # Apre la chat di gruppo
        elif message.startswith("GROUP_MESSAGE|"):
            # Estrae dettagli di un messaggio di gruppo
            _, sender_username, msg_content = message.split("|", 2)
            if sender_username != self.username:  # Ignora messaggi inviati dall'utente corrente
                group_key = ",".join(sorted(self.group_chats.keys()))  # Genera chiave per la chat di gruppo
                if group_key in self.group_chats:
                    self.group_chats[group_key].receive_message(f"{sender_username}: {msg_content}")
                else:
                    self.open_group_chat([sender_username])
                    if group_key in self.group_chats:
                        self.group_chats[group_key].receive_message(f"{sender_username}: {msg_content}")
        elif message.startswith("PRIVATE_MESSAGE|"):
            _, sender_username, msg_content = message.split("|", 2)
            if sender_username in self.private_chats:
                self.private_chats[sender_username].receive_message(f"{sender_username}: {msg_content}")
            else:
                self.open_private_chat(sender_username)
                self.private_chats[sender_username].receive_message(f"{sender_username}: {msg_content}")
        else:
            self.received_messages.append(message)  # Visualizza messaggi pubblici nella finestra principale

    def open_private_chat(self, target_username):
        """Apre una finestra di chat privata con un utente specifico, se non già aperta.

        Parametri:
            - target_username: Nome dell'utente con cui avviare la chat privata.
        """
        if target_username not in self.private_chats or not self.private_chats[target_username].isVisible():
            private_chat = PrivateChatWindow(self.username, [target_username], self.peer_network)
            private_chat.show()  # Mostra la finestra della chat privata
            self.private_chats[target_username] = private_chat  # Memorizza la finestra nel dizionario
        else:
            self.private_chats[target_username].activateWindow()  # Porta la finestra esistente in primo piano

    def open_group_chat(self, target_usernames):
        """Apre una finestra di chat di gruppo con gli utenti specificati, se non già aperta.

        Parametri:
            - target_usernames: Lista dei nomi degli utenti con cui avviare la chat di gruppo.
        """
        group_key = ",".join(sorted(target_usernames))  # Chiave unica per identificare la chat di gruppo
        if group_key not in self.group_chats or not self.group_chats[group_key].isVisible():
            group_chat = GroupChatWindow(self.username, target_usernames, self.peer_network)
            group_chat.show()  # Mostra la finestra della chat di gruppo
            self.group_chats[group_key] = group_chat  # Memorizza la finestra nel dizionario
        else:
            self.group_chats[group_key].activateWindow()  # Porta la finestra esistente in primo piano

    def update_connected_users(self):
        """Aggiorna e visualizza la lista degli utenti connessi."""
        connected_users_info = self.peer_network.get_connected_ips()
        user_list = "\n".join([f"{ip}: {username}" for ip, username in connected_users_info.items()])
        self.connected_users_display.setPlainText(user_list)  # Visualizza la lista degli utenti connessi


class MessageReceiver(QThread):
    """
    La classe MessageReceiver rappresenta un thread che si occupa di ricevere messaggi dalla rete peer-to-peer.

    Attributi:
        - message_received: Segnale emesso quando viene ricevuto un messaggio, contenente il messaggio come stringa.

    Metodi:
        - __init__(self, peer_network, parent=None): Costruttore che inizializza il thread con la rete peer-to-peer.
        - run(self): Metodo che avvia il server per ascoltare i messaggi in arrivo sulla rete peer-to-peer.
    """

    message_received = pyqtSignal(str)  # Segnale emesso quando viene ricevuto un messaggio

    def __init__(self, peer_network, parent=None):
        """Inizializza il thread MessageReceiver, configurandolo per ricevere messaggi dalla rete peer-to-peer.

        Parametri:
            - peer_network: Oggetto che rappresenta la rete peer-to-peer per la comunicazione tra utenti.
            - parent: Oggetto genitore opzionale, utile per integrare il thread in altre strutture.
        """
        super().__init__(parent)  # Inizializza la classe base QThread
        self.peer_network = peer_network  # Rete peer-to-peer per la comunicazione

    def run(self):
        """Avvia il server TCP della rete peer-to-peer per ascoltare i messaggi in arrivo.

        Questo metodo rimane in ascolto dei messaggi sulla porta 5001, la porta predefinita per la comunicazione tra i peer.
        """
        self.peer_network.start_peer_server(5001)  # Avvia il server TCP sulla porta 5001 per la comunicazione
