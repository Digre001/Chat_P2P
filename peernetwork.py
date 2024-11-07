import socket
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class PeerNetwork(QObject):
    # Signal to communicate the received message to the UI
    message_received_signal = pyqtSignal(str)  # Emitted when a new message is received

    def __init__(self, broadcast_ip="192.168.1.255", port=5000, buffer_size=1024, peer_timeout=10):
        super().__init__()  # Necessary for QObject initialization
        self.BROADCAST_IP = broadcast_ip
        self.PORT = port
        self.BUFFER_SIZE = buffer_size
        self.PEER_LIST = {}  # Dictionary to track peers with username and last activity timestamp
        self.PEER_TIMEOUT = peer_timeout
        self.connected_ips = {}  # Mapping of IPs to usernames
        self.running = True

    # Function to broadcast presence to the network
    def broadcast_presence(self, username):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)

        message = username.encode()  # Encode username to send over broadcast

        while self.running:
            try:
                # Send the broadcast message with the username
                sock.sendto(message, (self.BROADCAST_IP, self.PORT))
                time.sleep(5)  # Broadcast every 5 seconds
            except Exception as e:
                print(f"Broadcast error: {e}")
                break

    # Function to listen for messages from other peers and update the peer list
    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.PORT))  # Listen on all network interfaces
        print(f"Listening on port {self.PORT}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(self.BUFFER_SIZE)
                peer_ip = addr[0]
                username = data.decode()  # Decode the incoming message to get the username
                
                # Add or update the peer in the PEER_LIST
                self.PEER_LIST[peer_ip] = {'username': username, 'last_seen': time.time()}  # Set last seen timestamp
                self.connected_ips[peer_ip] = username  # Map the IP to the username
                print(f"{username} connected from {peer_ip}. Connected peers: {len(self.PEER_LIST)}")
            except Exception as e:
                print(f"Receive error: {e}")
                break

    # Function to monitor peer status and remove inactive peers
    def update_peer_list(self):
        while self.running:
            time.sleep(1)  # Check every second
            current_time = time.time()
            peers_to_remove = []

            # Check for inactive peers
            for peer, info in self.PEER_LIST.items():
                last_seen = info['last_seen']  # Access the last_seen timestamp
                if current_time - last_seen > self.PEER_TIMEOUT:  # Peer inactive
                    peers_to_remove.append(peer)

            # Remove inactive peers
            for peer in peers_to_remove:
                del self.PEER_LIST[peer]
                del self.connected_ips[peer]  # Remove from connected IPs list too
                print(f"Peer {peer} disconnected. Connected peers: {len(self.PEER_LIST)}")

    # Function to start the peer-to-peer network
    def start(self, username):
        self.running = True
        # Thread to broadcast presence
        broadcast_thread = threading.Thread(target=self.broadcast_presence, args=(username,))
        broadcast_thread.daemon = True
        broadcast_thread.start()

        # Thread to listen for other peers
        listen_thread = threading.Thread(target=self.listen_for_peers)
        listen_thread.daemon = True
        listen_thread.start()

        # Thread to monitor peer status
        peer_monitor_thread = threading.Thread(target=self.update_peer_list)
        peer_monitor_thread.daemon = True
        peer_monitor_thread.start()

    # Function to stop the peer-to-peer network
    def stop(self):
        self.running = False
        print("Stopping P2P network...")

    def get_ip_by_username(self, username):
        """Restituisce l'indirizzo IP associato al nome utente."""
        for ip, user in self.connected_ips.items():
            if user == username:
                return ip
        return None  # Restituisce None se l'utente non è trovato

    # Function to get connected IPs
    def get_connected_ips(self):
        return self.connected_ips  # Return the dictionary of connected IPs and usernames

    # Function that starts the TCP server to receive messages
    def start_peer_server(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", port))  # Listen on all network interfaces
        server_socket.listen(5)
        print(f"Listening on port {port}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection established with {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    # Function to handle the client that sends a message
    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"Message received: {message}")
                if message.startswith("CHAT_CLOSED|"):
                    chat_id = message.split("|", 1)[1]
                    print(f"Chat {chat_id} has been closed and will be marked as inactive.")
                elif message.startswith("DISCONNECT|"):
                    chat_id = message.split("|", 1)[1]
                    print(f"Chat {chat_id} has been closed by the peer.")

                # Emit the signal to update the UI with the new message
                self.message_received_signal.emit(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
        finally:
            client_socket.close()

    # Function to send a message to another peer
    def send_message(self, peer_ip, peer_port, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip, peer_port))
            client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            client_socket.close()


    def send_chat_closed_notification(self, chat_id):
        """Sends a notification indicating that a specific chat window was closed."""
        message = f"CHAT_CLOSED|{chat_id}"
        for ip, _ in self.connected_ips.items():
            self.send_message(ip, 5001, message)

    def send_disconnection_notification(self, chat_id):
        """Sends a message to indicate that a chat window was closed."""
        # Broadcast to all peers that this chat is closed
        message = f"DISCONNECT|{chat_id}"
        for ip, _ in self.connected_ips.items():
            self.send_message(ip, 5001, message)