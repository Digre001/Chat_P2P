import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from user_manager import UserManager
from login_app import LoginApp

# Imposta la configurazione del logging
LOG_FILE = '../active_users.log'  # Specifica il percorso del tuo file di log
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def all_users_inactive(user_manager):
    users = user_manager.load_users()
    return all(user['status'] == 'inactive' for user in users.values())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_manager = UserManager()

    # Controlla se tutti gli utenti sono inattivi prima di eliminare il file di log
    if all_users_inactive(user_manager) and os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)  # Elimina il file di log se esiste

    window = LoginApp(user_manager)
    window.show()
    sys.exit(app.exec_())
