import os
import json

# Percosrso del file json contenente i dati degli utenti
USER_DATA = 'user_data.json'

# Funzione per caricare i dati degli utenti
def load_users():
    if os.path.exists(USER_DATA):
        with open(USER_DATA, 'r') as file:
            return json.load(file)
    return {}