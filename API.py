from flask import Flask, request, jsonify
import sqlite3
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)  # Crea un'istanza dell'applicazione Flask

DATABASE = 'user_data.db'  # Nome del file di database SQLite


def get_db():
    """Connette al database SQLite e restituisce l'oggetto di connessione."""
    conn = sqlite3.connect(DATABASE)  # Connette al database
    return conn  # Restituisce la connessione per operazioni successive


def generate_rsa_keys(key_size=2048):
    """Genera una coppia di chiavi RSA e le restituisce in formato PEM.

    Parametri:
        - key_size: Lunghezza della chiave RSA in bit (predefinito 2048).

    Restituisce:
        - private_key_pem: Chiave privata in formato PEM.
        - public_key_pem: Chiave pubblica in formato PEM.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Esponente standard per RSA
        key_size=key_size,  # Lunghezza della chiave
        backend=default_backend()  # Backend per la generazione della chiave
    )
    public_key = private_key.public_key()  # Estrae la chiave pubblica dalla chiave privata

    # Serializza la chiave privata in formato PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # Usato per compatibilità
        encryption_algorithm=serialization.NoEncryption()  # Chiave non criptata
    ).decode('utf-8')

    # Serializza la chiave pubblica in formato PEM
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo  # Formato per chiave pubblica
    ).decode('utf-8')

    return private_key_pem, public_key_pem  # Restituisce entrambe le chiavi


@app.route('/register', methods=['POST'])
def register_user():
    """Registra un nuovo utente con nome utente e password, generando chiavi RSA.

    Corpo della richiesta:
        - username: Il nome dell'utente.
        - password: La password dell'utente.

    Restituisce:
        - JSON con successo e messaggio.
    """
    data = request.get_json()  # Estrae i dati JSON dalla richiesta
    username = data.get('username')
    password = data.get('password')

    # Crea l'hash della password usando SHA-256
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Genera chiavi RSA per l'utente
    private_key_pem, public_key_pem = generate_rsa_keys(key_size=2048)  # Specifica la lunghezza qui

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Inserisce i dettagli dell'utente nel database
        cursor.execute("INSERT INTO users (username, password_hash, private_key, public_key) VALUES (?, ?, ?, ?)",
                       (username, password_hash, private_key_pem, public_key_pem))
        conn.commit()  # Conferma l'operazione
        return jsonify({"success": True, "message": f"User {username} registered successfully!"}), 201
    except sqlite3.IntegrityError:
        # Ritorna un errore se il nome utente è già in uso
        return jsonify({"success": False, "message": "Username already exists!"}), 409
    finally:
        conn.close()  # Chiude la connessione al database


@app.route('/login', methods=['POST'])
def login_user():
    """Autentica un utente con nome utente e password.

    Corpo della richiesta:
        - username: Il nome dell'utente.
        - password: La password dell'utente.

    Restituisce:
        - JSON con successo e messaggio.
    """
    data = request.get_json()  # Estrae i dati JSON dalla richiesta
    username = data.get('username')
    password = data.get('password')

    # Hash della password per la verifica
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db()
    cursor = conn.cursor()

    # Controlla nel database se l'utente esiste con l'hash della password corrispondente
    cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = cursor.fetchone()  # Ottiene i risultati

    if user:
        return jsonify({"success": True, "message": f"User {username} logged in successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password!"}), 401


@app.route('/initialize_database', methods=['POST'])
def initialize_database():
    """Crea la tabella `private_chats` per i messaggi privati se non esiste già.

    Restituisce:
        - JSON con successo e messaggio.
    """
    conn = get_db()
    cursor = conn.cursor()
    # Crea la tabella per i messaggi privati se non esiste
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()  # Conferma la creazione della tabella
    conn.close()  # Chiude la connessione
    return jsonify({"success": True, "message": "Table private_chats initialized successfully!"}), 201


@app.route('/save_message', methods=['POST'])
def save_message():
    """Salva un messaggio privato nella tabella `private_chats`.

    Corpo della richiesta:
        - sender: Mittente del messaggio.
        - receiver: Destinatario del messaggio.
        - message: Contenuto del messaggio.

    Restituisce:
        - JSON con successo e messaggio.
    """
    data = request.get_json()  # Ottiene i dati JSON dalla richiesta
    sender = data.get('sender')
    receiver = data.get('receiver')
    message = data.get('message')

    conn = get_db()
    cursor = conn.cursor()

    # Inserisce il messaggio nel database
    cursor.execute('''
        INSERT INTO private_chats (sender, receiver, message)
        VALUES (?, ?, ?)
    ''', (sender, receiver, message))
    conn.commit()  # Conferma l'inserimento
    conn.close()

    return jsonify({"success": True, "message": "Message saved successfully!"}), 201


@app.route('/load_messages', methods=['GET'])
def load_messages():
    """Carica i messaggi tra due utenti in ordine di timestamp.

    Parametri della richiesta:
        - user1: Uno degli utenti.
        - user2: L'altro utente.

    Restituisce:
        - JSON con successo e lista di messaggi.
    """
    user1 = request.args.get('user1')  # Ottiene user1 dai parametri della richiesta
    user2 = request.args.get('user2')  # Ottiene user2 dai parametri della richiesta

    conn = get_db()
    cursor = conn.cursor()
    # Seleziona i messaggi scambiati tra user1 e user2
    cursor.execute('''
        SELECT sender, message, timestamp FROM private_chats
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp
    ''', (user1, user2, user2, user1))
    messages = cursor.fetchall()  # Ottiene tutti i messaggi trovati
    conn.close()

    return jsonify({"success": True, "messages": messages}), 200


@app.route('/get_public_key/<username>', methods=['GET'])
def get_public_key(username):
    """Ottiene solo la chiave pubblica di un utente.

    Parametri della richiesta:
        - username: Nome dell'utente.

    Restituisce:
        - JSON contenente la chiave pubblica dell'utente.
    """
    conn = get_db()
    cursor = conn.cursor()
    # Cerca la chiave pubblica dell'utente
    cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"public_key": result[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/get_private_key/<username>', methods=['GET'])
def get_private_key(username):
    """Ottiene solo la chiave privata di un utente.

    Parametri della richiesta:
        - username: Nome dell'utente.

    Restituisce:
        - JSON contenente la chiave privata dell'utente.
    """
    conn = get_db()
    cursor = conn.cursor()
    # Cerca la chiave privata dell'utente
    cursor.execute("SELECT private_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"private_key": result[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404


if __name__ == '__main__':
    # Crea il database e le tabelle `users` e `private_chats` se non esistono
    conn = get_db()
    cursor = conn.cursor()
    # Crea la tabella `users` per gli utenti se non esiste
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            private_key TEXT NOT NULL,
            public_key TEXT NOT NULL
        )
    ''')
    # Crea la tabella `private_chats` per i messaggi privati se non esiste
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()  # Conferma la creazione delle tabelle
    conn.close()

    app.run(host='0.0.0.0', port=5003)  # Esegue l'applicazione su tutte le interfacce di rete alla porta 5003
