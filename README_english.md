# Peer-to-Peer Chat Application

This application is a peer-to-peer messaging platform on local networks, designed to enable secure communication between users connected to the same network. The platform supports global, private, and group chats, using RSA encryption to ensure privacy in private chats. The backend is managed using Flask, while the user interface is developed with PyQt5.

## Table of Contents

- [Project Objective](#project-objective)
- [Main Features](#main-features)
- [Technologies Used](#technologies-used)
- [Code Structure](#code-structure)
- [Main File Analysis](#main-file-analysis)
- [System Architecture](#system-architecture)
- [Security](#security)
- [Limitations and Improvements](#limitations-and-improvements)
- [Testing](#testing)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Launching the Program](#launching-the-program)

---

## Project Objective

The application was created to facilitate secure communication between users connected to the same local network. It supports three main chat modes:
- **Global Chat**: visible to all users connected to the network.
- **Group Chat**: unencrypted conversation among multiple selected users.
- **Private Chat**: secure communication between two users, protected by RSA encryption for maximum privacy.

The main goal is to provide a secure and easy-to-use tool for private or group communication, ensuring that messages are only visible to the intended recipients.

---

## Main Features

- **Registration and Login**: Users can register and log in using a username and password. The password is encrypted and stored securely.
- **RSA Encryption**: Each user has an RSA key pair (private and public) that are used to encrypt and decrypt messages.
- **Private and Group Messages**: Users can send private messages to other users or create group chats.
- **Peer-to-Peer Network**: Utilizes peer-to-peer technology to send and receive messages between users, making communication secure and decentralized.

### Security and Encryption
- **RSA Encryption for Private Chats**: All messages sent in private chats are encrypted with RSA, ensuring that only the recipient can read the content. Each user generates an RSA key pair (public and private) upon registration.
- **Secure Key Management**: A user's public key is shared to encrypt messages intended for them, while their private key is kept secure to decrypt only the received messages.

### Intuitive Interface
- **PyQt5 Interface**: A graphical interface developed with PyQt5 allows users to easily manage chats, view connected users, and send messages in real-time.
- **Real-Time Chat**: The interface provides real-time updates for messages and the list of online users, ensuring smooth communication.

### User Management
- **Registration and Login**: Each user can register or log in via a secure authentication system, with encrypted passwords stored in the database.
- **Connected User List**: Displays in real-time the users available for private or group chats.

### Data Persistence
- **SQLite Database**: The platform uses SQLite to persistently store user and message data, ensuring that all information is available even after the application restarts.

### Peer-to-Peer Communication
- **Peer-to-Peer Network**: Uses a peer-to-peer protocol to allow direct communication between devices on the same local network, eliminating the need for a central server.

---

## Technologies Used

- **Flask**: For the backend and API management.
- **PyQt5**: For the graphical user interface (GUI).
- **SQLite**: Database for data persistence.
- **RSA**: Asymmetric encryption algorithm to ensure security in private chats.
- **TCP/UDP**: Protocols for peer-to-peer communication.

---

## Code Structure

### File Structure

| File               | Description                                                                                             |
|--------------------|---------------------------------------------------------------------------------------------------------|
| `API.py`           | Flask API server for user and message management, with RSA encryption support. |
| `chat_windows.py`  | Defines chat windows for private and group communications.                                |
| `login_app.py`     | Manages the login and registration window via PyQt5 and interaction with the API.                   |
| `main.py`          | Main entry point, launches the user interface.                                            |
| `message_app.py`   | Main messaging application for the global chat.                                          |
| `peernetwork.py`   | Manages the peer-to-peer communication protocol.                                                  |
| `user_manager.py`  | Interacts with the API for registration, authentication, and key management.                       |
| `user_data.db`     | SQLite database for storing users and messages.                                               |
| `requirements.txt` | List of dependencies.                                                                               |

---

## Main File Analysis

### `API.py`
This file implements the Flask API server for managing the main operations:
- **User management routes**: `/register` and `/login` for registering and authenticating users.
- **RSA key management**: `/get_public_key` and `/get_private_key` to retrieve the necessary keys for private chats.
- **Message management**: `/save_message` and `/load_messages` to save and retrieve messages from the database.

### `chat_windows.py`
Defines the PyQt5 windows for the chat:
- **Private Chat**: Uses the recipient's public key to encrypt messages.
- **Group Chat**: Sends unencrypted messages to multiple recipients.
- Provides an intuitive user interface for managing chat and viewing connected users.

### `login_app.py`
Manages the login window:
- Allows registration and login via API calls.
- After authentication, the user is redirected to the main messaging window.

### `main.py`
Main entry point file:
- Configures network variables and launches the main user interface.

### `message_app.py`
Main messaging component:
- Displays the global chat and the list of connected users.
- Automatically updates the user list and received messages.

### `peernetwork.py`
Module for peer-to-peer communication:
- Uses broadcasting to detect and connect devices on the local network (UDP).
- Manages the transmission and reception of messages (TCP).

### `user_manager.py`
Handles API functions for user registration and authentication:
- Registers and authenticates users via API requests.
- Provides the RSA keys for users in private chats.

### `requirements.txt`
Includes the project's main dependencies:
- **Flask** for the API server
- **PyQt5** for the graphical interface
- **cryptography** for RSA encryption
- **requests** for HTTP communications between the application and the API server.

---

## System Architecture

The application architecture is based on a modular structure that separates the network logic (managed by Flask and the peer-to-peer module) from the GUI (PyQt5). The main components of the architecture are:
1. **Backend (Flask)**: An API server for managing authentication logic, encryption, and message persistence.
2. **Frontend (PyQt5)**: A user interface that facilitates interaction and message management.
3. **Database (SQLite)**: Persists information about users and messages.
4. **Peer-to-Peer Network**: Managed by the `peernetwork.py` module, enabling users to detect other devices on the same local network and establish connections for secure communication.

## Security

- **RSA for Private Chats**: The security of private chats depends on the management of RSA keys; ensure that private keys are not accessible by others.
- **Secure Password Storage**: Passwords are encrypted with hashing (SHA-256) before being stored.

---

## Limitations and Implementations

### Current Limitations
- **Local Network Only**: This application works exclusively on local networks, limiting its use in wider network contexts.
- **API Security**: Currently, the Flask server is configured for development environments. For production environments, it is recommended to implement advanced security measures.
- **Limited Scalability**: The peer-to-peer architecture is more suited for small networks, such as home or business LANs.

### Future Implementations
- **Encryption Optimization**: Use temporary symmetric keys for group chats to improve security without burdening the system.
- **UI Improvements**: The interface could be enhanced with new features like message status notifications, advanced user visualization, and customizable themes.
- **URL Management**: Replace `<ip_server>` with the local IP address of the server automatically.

---

## Testing

**Interface Testing**:
   - The graphical part can be manually tested to ensure that all features are accessible and work correctly.

---

## Prerequisites

Ensure that the following are installed:

- *Python 3.10 or higher*
- *pip*: Python package manager
- *Virtualenv* (recommended): To create a virtual environment

---

## Installation

1. **Clone the repository**:

   Open the terminal and run the following command to clone the repository:

   ```bash
   git clone https://github.com/Digre001/Chat_P2P.git
   


2. **Install the dependencies**:

   Make sure `pip` is installed. Install all required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```
## Launching the Program

1. **Start the Flask server**:

   Run the API server to handle the backend of the application (only on one machine):

   ```bash
   python3 API.py
   ```

Once started, the server will be accessible at [http://<ip_server>:5003]. <br> 
Replace `<ip_server>` with the local IP address of the server, if needed. 
Replace the URL generated by the API in the `user_manager.py` and `chat_windows.py` files to ensure proper communication between the modules. 
Also, replace the broadcast IP address of your computer in the peernetwork.py file to ensure proper communication between devices.
   <br> <br>

2. **Start the graphical interface**: <br>
   **fter performing all the previous replacements in the various files, then:**<br>
   Run the main file to open the graphical user interface of the application:

   ```bash
   python3 main.py
   ```

   A window will open where you can use the application's features, including global chat, private chats, and group chats. <br> <br>

3. **Registration and Login**:
   - Create a new account to start using the application.
   - Log in with the created credentials to access the main chat.<br><br>

4. **Account già nel database**
   | **Username**       | **Password**                |
   |--------------------|-----------------------------|
   | `fabio`            | `digregorio`                |
   | `lorenzo`          | `pagliaricci`               |
   | `virginia`         | `simoncini`                 |




