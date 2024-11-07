from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
from message_app import MessageApp, MessageReceiver

# Classe della finestra di login
class LoginApp(QWidget):
    def __init__(self, user_manager, peer_network): # Aggiungiamo il peer_network come parametro
        super().__init__() # Chiama il costruttore della classe madre
        self.user_manager = user_manager # Salva il riferimento all'oggetto UserManager
        self.peer_network = peer_network # Salva il riferimento all'oggetto PeerNetwork
        self.init_ui() # Inizializza l'interfaccia grafica

# Metodo per inizializzare l'interfaccia grafica
    def init_ui(self): 
        # Layout principale
        layout = QVBoxLayout()

        # Etichetta e campo di input per il nome utente
        self.label_username = QLabel("Username:")
        layout.addWidget(self.label_username) # Aggiungi l'etichetta al layout
        self.username_field = QLineEdit() # Crea il campo di input per il nome utente
        self.username_field.setPlaceholderText("Username") # Testo di esempio nel campo di input
        layout.addWidget(self.username_field) # Aggiungi il campo di input al layout

        # Etichetta e campo di input per la password
        self.label_password = QLabel("Password:")
        layout.addWidget(self.label_password) # Aggiungi l'etichetta al layout
        self.password_field = QLineEdit() # Crea il campo di input per la password
        self.password_field.setPlaceholderText("Password") # Testo di esempio nel campo di input
        self.password_field.setEchoMode(QLineEdit.Password) # Nasconde i caratteri della password
        layout.addWidget(self.password_field) # Aggiungi il campo di input al layout

        # Aggiunge uno spazio vuoto tra il campo password e i pulsanti 
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding) # 20 pixel di larghezza, 40 pixel di altezza 
        layout.addItem(spacer) # Aggiungi lo spazio vuoto al layout

        # Pulsante per il login
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user) # Associa il click del pulsante al metodo login_user
        layout.addWidget(self.login_button) # Aggiungi il pulsante al layout

        # Bottone di registrazione
        self.btn_register = QPushButton("Registrati") # Crea il pulsante di registrazione
        self.btn_register.clicked.connect(self.register_user) # Associa il click del pulsante al metodo register_user
        layout.addWidget(self.btn_register) # Aggiungi il pulsante al layout


        # Collega il tasto "Invio" al pulsante di login sia per il campo username che per la password
        self.username_field.returnPressed.connect(self.login_user) 
        self.password_field.returnPressed.connect(self.login_user) 

        # Imposta il layout e il titolo della finestra
        self.setLayout(layout)
        self.setWindowTitle("Login System") # Imposta il titolo della finestra

    # Metodo per registrare un nuovo utente
    def register_user(self):
        username = self.username_field.text() # Ottiene il testo inserito nel campo username
        password = self.password_field.text()  # Ottiene il testo inserito nel campo password
        success, msg = self.user_manager.register_user(username, password) # Effettua la registrazione tramite user_manager
        QMessageBox.information(self, "Registrazione", msg) # Mostra un messaggio informativo con il risultato

    # Metodo per il login di un utente
    def login_user(self):
        username = self.username_field.text() # Ottiene il testo inserito nel campo username
        password = self.password_field.text()  # Ottiene il testo inserito nel campo password
        success, msg = self.user_manager.login_user(username, password) # Effettua il login tramite user_manager
        if success:
            self.peer_network.start(username)  # Avvia il network peer-to-peer con il nome utente
            self.open_message_app(username) # Avvia il network peer-to-peer con il nome utente
        else:
            QMessageBox.warning(self, "Errore", msg)  # Mostra un messaggio di errore se il login fallisce

    # Metodo per aprire l'applicazione dei messaggi
    def open_message_app(self, username):
        self.message_app = MessageApp(username, self.user_manager, self.peer_network)  # Crea l'istanza dell'app di messaggi
        self.message_app.show()  # Mostra la finestra dell'app di messaggi
        self.close()  # Chiude la finestra di login
