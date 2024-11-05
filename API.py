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
    conn.commit()
    conn.close()
    
    app.run(host='0.0.0.0', port=5003)  # Accesso LAN