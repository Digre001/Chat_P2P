from flask import Flask, request, jsonify
import sqlite3
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

DATABASE = 'user_data.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def generate_rsa_keys(key_size=2048):
    # Genera una coppia di chiavi RSA con lunghezza standard
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    
    # Serializza le chiavi per memorizzarle nel database
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # Usato per compatibilità
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_key_pem, public_key_pem

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Hash della password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Genera chiavi RSA per l'utente
    private_key_pem, public_key_pem = generate_rsa_keys(key_size=2048)  # Specifica la lunghezza qui
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash, private_key, public_key) VALUES (?, ?, ?, ?)",
                       (username, password_hash, private_key_pem, public_key_pem))
        conn.commit()
        return jsonify({"success": True, "message": f"User {username} registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists!"}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = cursor.fetchone()
    
    if user:
        return jsonify({"success": True, "message": f"User {username} logged in successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password!"}), 401

##### per richieste messaggi database#####

@app.route('/initialize_database', methods=['POST'])
def initialize_database():
    """Endpoint per creare la tabella private_chats se non esiste."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Table private_chats initialized successfully!"}), 201

@app.route('/save_message', methods=['POST'])
def save_message():
    data = request.get_json()
    sender = data.get('sender')
    receiver = data.get('receiver')
    message = data.get('message')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO private_chats (sender, receiver, message)
        VALUES (?, ?, ?)
    ''', (sender, receiver, message))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Message saved successfully!"}), 201

@app.route('/load_messages', methods=['GET'])
def load_messages():
    user1 = request.args.get('user1')
    user2 = request.args.get('user2')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, message, timestamp FROM private_chats
        WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
        ORDER BY timestamp
    ''', (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()

    return jsonify({"success": True, "messages": messages}), 200

@app.route('/get_keys/<username>', methods=['GET'])
def get_keys(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT private_key, public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"public_key": result[1], "private_key": result[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@app.route('/get_public_key/<username>', methods=['GET'])
def get_public_key(username):
    """Endpoint per ottenere solo la chiave pubblica di un utente."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"public_key": result[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/get_private_key/<username>', methods=['GET'])
def get_private_key(username):
    """Endpoint per ottenere solo la chiave privata di un utente."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT private_key FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"private_key": result[0]}), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
if __name__ == '__main__':
    # Crea il database e la tabella se non esistono
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            private_key TEXT NOT NULL,
            public_key TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS private_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    app.run(host='0.0.0.0', port=5003)  # Accesso LAN