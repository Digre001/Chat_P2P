import sys
import os
import json
from PyQt5.QtWidgets import QApplication
from Codici.user_manager import UserManager
from Codici.login_app import LoginApp


def delete_log_if_all_users_inactive():
    # Path to the user.json file inside the Dati folder
    user_file = os.path.join(os.path.dirname(__file__), 'Dati/user.json')

    if os.path.exists(user_file):
        with open(user_file, 'r') as file:
            try:
                users = json.load(file)
                all_inactive = all(user['status'] == 'inactive' for user in users.values())

                if all_inactive:
                    # Path to the chat_log.txt file inside the Dati folder
                    log_file = os.path.join(os.path.dirname(__file__), 'Dati/active_users.log')
                    if os.path.exists(log_file):
                        os.remove(log_file)
                        print("File di log eliminato.")
            except json.JSONDecodeError:
                print("Errore nella lettura del file JSON.")


if __name__ == '__main__':
    # Elimina il file di log se tutti gli utenti sono inattivi
    delete_log_if_all_users_inactive()

    # Avvia l'applicazione Qt
    app = QApplication(sys.argv)
    user_manager = UserManager()  # Istanza di UserManager
    window = LoginApp(user_manager)  # Mostra la finestra di login
    window.show()
    sys.exit(app.exec_())

