from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

DATABASE = 'user_data.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Hash the password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
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
    # Create the database and table if they don't exist
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    
    app.run(host='0.0.0.0', port=5003)  # Set to 0.0.0.0 to allow access from other computers in the LAN
