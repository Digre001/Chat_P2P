from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
from Codici.chat_window import ChatWindow  # Modifica l'import per riflettere la struttura delle cartelle

class LoginApp(QWidget):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_username = QLabel("Username:")
        layout.addWidget(self.label_username)
        self.entry_username = QLineEdit()
        layout.addWidget(self.entry_username)

        self.label_password = QLabel("Password:")
        layout.addWidget(self.label_password)
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.entry_password)

        # Connetti il tasto "Invio" al metodo di login
        self.entry_password.returnPressed.connect(self.login_user)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.login_user)
        layout.addWidget(self.btn_login)

        self.btn_register = QPushButton("Registrati")
        self.btn_register.clicked.connect(self.register_user)
        layout.addWidget(self.btn_register)

        self.setLayout(layout)
        self.setWindowTitle("Login System")

    def register_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Errore", "Inserisci almeno un carattere per nome utente e password!")
            return

        success, msg = self.user_manager.register_user(username, password)
        QMessageBox.information(self, "Registrazione", msg)

    def login_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()
        success, msg = self.user_manager.login_user(username, password)
        if success:
            QMessageBox.information(self, "Login", msg)
            self.chat_window = ChatWindow(username, self.user_manager)
            self.chat_window.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Errore", msg)
