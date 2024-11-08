from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import requests
BASE_URL = 'http://172.20.10.5:5003'  # Indirizzo API

# Funzione per recuperare la chiave pubblica di un utente specifico dal database
def get_public_key(username):
    """Richiede la chiave pubblica di un utente tramite l'API."""
    response = requests.get(f"{BASE_URL}/get_public_key/{username}") # Effettua una richiesta GET all'API per ottenere la chiave pubblica dell'utente specificato
    if response.status_code == 200:  # Verifica se la risposta ha avuto successo (status code 200)
        public_key_pem = response.json().get("public_key")  # Estrae la chiave pubblica in formato PEM dal JSON della risposta
         # Se la chiave pubblica è presente, la converte in un oggetto di tipo 'public key'
        if public_key_pem:
            return serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
         # Se non è riuscito a ottenere la chiave pubblica, ritorna None
    return None
# Funzione per recuperare la chiave privata di un utente specifico dal database
def get_private_key(username):
    """Richiede la chiave privata di un utente tramite l'API."""
    response = requests.get(f"{BASE_URL}/get_private_key/{username}")  # Effettua una richiesta GET all'API per ottenere la chiave privata dell'utente specificato
    if response.status_code == 200: # Verifica se la risposta ha avuto successo (status code 200)
        private_key_pem = response.json().get("private_key")   # Estrae la chiave privata in formato PEM dal JSON della risposta
        if private_key_pem:  # Se la chiave privata è presente, la converte in un oggetto di tipo 'private key'
            print(f"Private key fetched successfully for {username}.")
            return serialization.load_pem_private_key(private_key_pem.encode('utf-8'), password=None)
         # Se non è riuscito a ottenere la chiave privata, stampa un messaggio di errore e ritorna None
    print(f"Failed to fetch private key for {username}: {response.json().get('message', 'Unknown error')}")
    return None

# Funzione per inizializzare il database, in particolare per creare la tabella "private_chats"
def initialize_database():
    """Effettua una richiesta all'API per inizializzare la tabella private_chats."""
    response = requests.post(f"{BASE_URL}/initialize_database")
     # Verifica se la risposta ha avuto successo (status code 201, risorsa creata)
    if response.status_code == 201:
        print("Database initialized successfully!")
    else:  # In caso di errore, stampa un messaggio specifico o un messaggio di errore generico
        print("Failed to initialize database:", response.json().get("message", "Unknown error"))

# Funzione per salvare un messaggio nel database inviandolo all'API
def save_message_to_db(sender, receiver, message):
    """Invia un messaggio in chiaro all'API per salvarlo nel database."""
    # Crea un dizionario con i dati del messaggio da inviare
    data = {
        "sender": sender,  # Mittente del messaggio
        "receiver": receiver, # Destinatario del messaggio
        "message": message  # Contenuto del messaggio
    }
    response = requests.post(f"{BASE_URL}/save_message", json=data)  # Effettua una richiesta POST all'API per salvare il messaggio nel database
    return response.json()     # Restituisce la risposta JSON dell'API

# Funzione per caricare i messaggi tra due utenti dal database utilizzando l'API
def load_messages_from_db(user1, user2):
    """Carica i messaggi tra due utenti dal database tramite l'API."""
     # Crea un dizionario con i parametri per specificare gli utenti coinvolti nella conversazione
    params = {
        "user1": user1, # Primo utente
        "user2": user2 # Secondo utente
    }
    response = requests.get(f"{BASE_URL}/load_messages", params=params) # Effettua una richiesta GET all'API per ottenere i messaggi tra i due utenti
    if response.status_code == 200:  # Se la risposta ha avuto successo (status code 200), restituisce i messaggi in formato JSON
        return response.json()["messages"]
    else:
        return []  # In caso di errore, restituisce una lista vuota

# Funzione per caricare le chiavi RSA (pubblica e privata) di un utente tramite l'API
def load_user_keys(username):
    """Carica le chiavi RSA dell'utente tramite l'API."""
    # Effettua una richiesta GET all'API per ottenere le chiavi dell'utente specificato
    response = requests.get(f"{BASE_URL}/get_keys/{username}")
     # Se la risposta ha avuto successo (status code 200), estrae i dati dal JSON della risposta
    if response.status_code == 200:
        data = response.json()
        return data.get("public_key"), data.get("private_key")  # Restituisce la chiave pubblica e la chiave privata dell'utente
    return None, None # Se non è riuscito a ottenere le chiavi, restituisce None per entrambe


# Esempio di utilizzo nella classe PrivateChatWindow
class PrivateChatWindow(QWidget):
# Segnale che viene emesso quando la finestra viene chiusa
    closed_signal = pyqtSignal()

    def __init__(self, username, target_users, peer_network): 
        # Inizializza la finestra del widget e chiama il costruttore della classe base
        super().__init__()
        self.username = username  # Assegna l'username dell'utente
         # Assegna la lista degli utenti target (destinatari del messaggio) 
        self.target_users = target_users   # lista degli utenti destinatari
        self.peer_network = peer_network  # Assegna l'oggetto peer_network, utilizzato per gestire la comunicazione tra utenti
        self.init_ui()  # Inizializza l'interfaccia grafica
        # Carica i messaggi precedenti (chat passate) tra l'utente corrente e i destinatari
        self.load_previous_messages()       

# Funzione per inizializzare l'interfaccia utente (UI) della finestra di chat privata
    def init_ui(self):
        layout = QVBoxLayout()  # Crea un layout verticale per organizzare i widget
        chat_with = ", ".join(self.target_users)  # Unisce i nomi degli utenti target con una virgola per mostrarli nel titolo della finestra
        self.setWindowTitle(f"Private Chat with {chat_with}")

# Crea un'area di testo per visualizzare i messaggi ricevuti
        self.received_messages = QTextEdit() # Crea un'area di testo per visualizzare i messaggi ricevuti
        self.received_messages.setPlaceholderText("Receive messages here...")  # Imposta un testo di esempio
        self.received_messages.setReadOnly(True) # Imposta l'area di testo in sola lettura
        layout.addWidget(self.received_messages) # Aggiunge l'area di testo al layout

# Crea un campo di testo per l'inserimento dei messaggi
        self.input_message = QLineEdit()
        self.input_message.setPlaceholderText("Write a message...")    # Imposta un testo di esempio
        layout.addWidget(self.input_message) # Aggiunge il campo di testo al layout
        self.input_message.returnPressed.connect(self.send_message) # Collega il segnale 'returnPressed' all'invio del messaggio

# Crea un pulsante per inviare i messaggi
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message) # Collega il clic del pulsante all'invio del messaggio
        layout.addWidget(self.send_button) # Aggiunge il pulsante al layout

        self.setLayout(layout) # Imposta il layout per la finestra di chat

# Funzione per caricare i messaggi precedenti tra l'utente corrente e i destinatari
    def load_previous_messages(self):
        for target_user in self.target_users: # Itera su tutti gli utenti target
            messages = load_messages_from_db(self.username, target_user) # Carica i messaggi tra l'utente corrente e il destinatario
            for sender, message, timestamp in messages:  # Usa 'message' invece di 'encrypted_message' # Itera su tutti i messaggi
                if sender == self.username: # Se il mittente è l'utente corrente
                    display_message = message  # Mostra il messaggio in chiaro
                else: # Se il mittente è il destinatario
                    display_message = message  # Mostra il messaggio cifrato (o in chiaro, se disponibile)
                self.received_messages.append(f"{sender} ({timestamp}): {display_message}") # Aggiunge il messaggio formattato con il mittente e il timestamp all'area di testo

# Funzione per inviare un messaggio
    def send_message(self):
        message = self.input_message.text()  # Ottiene il testo del messaggio dall'input
        if message: # Se il messaggio non è vuoto
            for target_username in self.target_users:   # Itera su tutti gli utenti target (destinatari)
                # Salva il messaggio in chiaro nel database
                save_message_to_db(self.username, target_username, message)

 # Recupera la chiave pubblica del destinatario
                public_key = get_public_key(target_username)
                if public_key: # Se la chiave pubblica è disponibile
                    # Cifra il messaggio con la chiave pubblica del destinatario
                    encrypted_message = public_key.encrypt( 
                        message.encode('utf-8'),  # Codifica il messaggio in bytes
                        padding.OAEP(  #utilizza il padding OAEP per la crittografia
                            mgf=padding.MGF1(algorithm=hashes.SHA256()), # Mask generation function basata su SHA256
                            algorithm=hashes.SHA256(),  # Algoritmo di hashing SHA256
                            label=None # Nessuna etichetta specificata
                    
                        )
                    )

                    # Converte il messaggio cifrato in formato esadecimale per l'invio tramite JSON
                    encrypted_message_hex = encrypted_message.hex()

                    # Invia il messaggio cifrato al destinatario tramite il peer network
                    ip = self.peer_network.get_ip_by_username(target_username) # Ottiene l'IP dell'utente target tramite il nome
                    if ip:
                        private_message = f"PRIVATE_MESSAGE|{self.username}|{encrypted_message_hex}"  # Crea il messaggio privato formattato con l'username e il messaggio cifrato in esadecimale
                        self.peer_network.send_message(ip, 5001, private_message)  # Invia il messaggio all'IP del destinatario sulla porta specificata

           # Mostra il messaggio inviato nella finestra di chat
            self.received_messages.append(f"{self.username}: {message}")
            self.input_message.clear()  #Pulisce il campo di input per nuovi messaggi

    def closeEvent(self, event): # Gestione dell'evento di chiusura della finestra
        self.closed_signal.emit() # Emette il segnale 'closed_signal' quando la finestra viene chiusa
        event.accept() # Accetta l'evento di chiusura

    def receive_message(self, message): # Funzione per gestire la ricezione di un messaggio dal peer network
        """Gestisce la ricezione di un messaggio dalla rete peer."""
        # Divide il messaggio per estrarre il mittente e il contenuto
        try:
            print(f"Received message pls pls pls: {message}")
             # Divide il messaggio su ': ' e considera il resto come il messaggio cifrato in esadecimale
            sender, encrypted_message_hex = message.split(': ', 1)   # Divide il messaggio su ': ' e considera il resto come il messaggio cifrato in esadecimale
            
          # Supponendo di avere logica per determinare il tipo di messaggio
            message_type = "PRIVATE_MESSAGE"  # Tipo di messaggio privato
            
            # Se il messaggio è un messaggio privato e il mittente è uno degli utenti target
            encrypted_message = bytes.fromhex(encrypted_message_hex.strip())  # Converte il messaggio cifrato da esadecimale a bytes per la decodifica

            # Recupera la chiave privata dell'utente corrente dal database
            private_key = get_private_key(self.username) 

            try: # Prova a decifrare il messaggio
                # Decifra il messaggio con la chiave privata dell'utente corrente
                decrypted_message = private_key.decrypt(
                    encrypted_message, # Messaggio cifrato
                    padding.OAEP( # Padding OAEP per la decrittografia
                        mgf=padding.MGF1(algorithm=hashes.SHA256()), # Mask generation function basata su SHA256
                        algorithm=hashes.SHA256(), # Algoritmo di hashing SHA256
                        label=None # Nessuna etichetta specificata
                    )
                ).decode('utf-8') # Decodifica il messaggio in formato UTF-8
                display_message = decrypted_message # Mostra il messaggio decifrato
            except Exception as e: # Se si verifica un errore durante la decrittografia
                print(f"Decryption failed: {e}") # Stampa un messaggio di errore
                display_message = "[Failed to decrypt message]" # Mostra un messaggio di errore

            # Mostra il messaggio ricevuto nella finestra di chat privata
            self.received_messages.append(f"{sender}: {display_message}")
            
        except ValueError: # Se si verifica un errore durante la divisione del messaggio
            print("Received an invalid message format") # Stampa un messaggio di errore

# Esempio di utilizzo nella classe GroupChatWindow 
class GroupChatWindow(QWidget):
    def __init__(self, username, group_users, peer_network): # Costruttore della classe GroupChatWindow
        super().__init__() # Chiama il costruttore della classe base
        self.username = username # Assegna l'username dell'utente
        self.group_users = group_users # Assegna la lista degli utenti del gruppo (destinatari del messaggio)
        self.peer_network = peer_network # Assegna l'oggetto peer_network, utilizzato per gestire la comunicazione tra utenti
        self.init_ui() # Inizializza l'interfaccia grafica

# Funzione per inizializzare l'interfaccia utente (UI) della finestra di chat di gruppo
    def init_ui(self):
        layout = QVBoxLayout() # Crea un layout verticale per organizzare i widget
        group_title = ", ".join(self.group_users) # Unisce i nomi degli utenti del gruppo con una virgola per mostrarli nel titolo della finestra
        self.setWindowTitle(f"Group Chat with {group_title}") # Imposta il titolo della finestra

# Crea un'area di testo per visualizzare i messaggi ricevuti
        self.received_messages = QTextEdit()
        self.received_messages.setPlaceholderText("Receive messages here...") # Imposta un testo di esempio
        self.received_messages.setReadOnly(True) # Imposta l'area di testo in sola lettura
        layout.addWidget(self.received_messages) # Aggiunge l'area di testo al layout

        self.input_message = QLineEdit() # Crea un campo di testo per l'inserimento dei messaggi
        self.input_message.setPlaceholderText("Write a message...") # Imposta un testo di esempio
        layout.addWidget(self.input_message) # Aggiunge il campo di testo al layout
        self.input_message.returnPressed.connect(self.send_message) # Collega il segnale 'returnPressed' all'invio del messaggio

        self.send_button = QPushButton("Send") # Crea un pulsante per inviare i messaggi
        self.send_button.clicked.connect(self.send_message) # Collega il clic del pulsante all'invio del messaggio
        layout.addWidget(self.send_button) # Aggiunge il pulsante al layout

        self.setLayout(layout) # Imposta il layout per la finestra di chat di gruppo

# Funzione per inviare un messaggio al gruppo
    def send_message(self):
        message = self.input_message.text() # Ottiene il testo del messaggio dall'input
        if message:
            # Mostra il messaggio nella chat
            self.received_messages.append(f"{self.username}: {message}")
            for target_username in self.group_users: # Itera su tutti gli utenti del gruppo
                ip = self.peer_network.get_ip_by_username(target_username) # Ottiene l'IP dell'utente target tramite il nome
                if ip: 
                    group_message = f"GROUP_MESSAGE|{self.username}|{message}" # Crea il messaggio di gruppo formattato con l'username e il messaggio
                    self.peer_network.send_message(ip, 5001, group_message)  # Invia un messaggio al dispositivo dell'utente nella rete peer tramite peer_network (indirizzo IP destinatario, numero porta destinatario, contenuto del messaggio)
            self.input_message.clear() # Pulisce il campo di input dopo l'invio del messaggio

# Funzione per ricevere un messaggio di gruppo e visualizzarlo
    def receive_message(self, message):
        self.received_messages.append(message) # Aggiunge il messaggio ricevuto direttamente alla finestra di chat
