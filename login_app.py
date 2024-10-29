from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QSpacerItem, QSizePolicy
from message_app import MessageApp, MessageReceiver

# Login Window Class
class LoginApp(QWidget):
    def __init__(self, user_manager, peer_network):
        super().__init__()
        self.user_manager = user_manager
        self.peer_network = peer_network
        self.init_ui()

    def init_ui(self):
        # Layout principale
        layout = QVBoxLayout()

        # Label e campo per il nome utente
        self.label_username = QLabel("Username:")
        layout.addWidget(self.label_username)
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Username")
        layout.addWidget(self.username_field)

        # Label e campo per la password
        self.label_password = QLabel("Password:")
        layout.addWidget(self.label_password)
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Password")
        self.password_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_field)

        # Aggiungi uno spazio vuoto tra password e pulsanti
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # Bottone di registrazione
        self.btn_register = QPushButton("Registrati")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register)

        # Bottone di login
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        # Imposta il layout
        self.setLayout(layout)
        self.setWindowTitle("Login System")

    # Metodo per la registrazione di un utente
    def register_user(self):
        username = self.username_field.text()
        password = self.password_field.text()
        success, msg = self.user_manager.register_user(username, password)
        QMessageBox.information(self, "Registrazione", msg)

    # Metodo per il login di un utente
    def login_user(self):
        username = self.username_field.text()
        password = self.password_field.text()
        success, msg = self.user_manager.login_user(username, password)

        if success:
            self.peer_network.start(username)  # Avvia il network con il nome utente
            self.open_message_app(username)
        else:
            QMessageBox.warning(self, "Errore", msg)

    # Metodo per aprire l'app dei messaggi
    def open_message_app(self, username):
        self.message_app = MessageApp(username, self.user_manager, self.peer_network)
        self.message_app.show()
        self.close()
