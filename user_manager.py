import requests  # Importa il modulo per fare richieste HTTP

class UserManager:
    BASE_URL = 'http://192.168.178.220:5003'  # L'URL di base del server API per la gestione degli utenti, da aggiornare con l'indirizzo corretto

    def register_user(self, username, password):
        """
        Questo metodo si occupa della registrazione di un nuovo utente.
        
        :param username: Il nome utente che l'utente vuole registrare.
        :param password: La password che l'utente sceglie di associare al proprio account.
        
        :return: Una tupla contenente un valore booleano (True se la registrazione ha avuto successo, False altrimenti)
                 e un messaggio di risposta proveniente dall'API (es. "Registrazione completata" o errore).
        """
        # Invia una richiesta HTTP POST all'API per registrare l'utente con il nome utente e la password specificati
        response = requests.post(f"{self.BASE_URL}/register", json={"username": username, "password": password})
        
        # Verifica se la registrazione è avvenuta con successo (status code 201 indica una creazione riuscita)
        if response.status_code == 201:
            return True, response.json()["message"]  # Restituisce True e il messaggio di successo
        return False, response.json()["message"]  # Se la registrazione non ha avuto successo, restituisce False e il messaggio di errore

    def login_user(self, username, password):
        """
        Questo metodo gestisce il login di un utente già registrato.

        :param username: Il nome utente con cui l'utente tenta di effettuare il login.
        :param password: La password corrispondente al nome utente fornito.

        :return: Una tupla contenente un valore booleano (True se il login è riuscito, False altrimenti)
                 e un messaggio di risposta proveniente dall'API (es. "Login riuscito" o errore).
        """
        # Invia una richiesta HTTP POST all'API per il login con il nome utente e la password forniti
        response = requests.post(f"{self.BASE_URL}/login", json={"username": username, "password": password})
        
        # Verifica se il login è riuscito (status code 200 indica che il login è andato a buon fine)
        if response.status_code == 200:
            return True, response.json()["message"]  # Restituisce True e il messaggio di successo
        return False, response.json()["message"]  # Se il login fallisce, restituisce False e il messaggio di errore

