import socket
import threading
import time

class PeerNetwork:
    def __init__(self, broadcast_ip="192.168.178.255", port=5000, buffer_size=1024, peer_timeout=10):
        self.BROADCAST_IP = broadcast_ip
        self.PORT = port
        self.BUFFER_SIZE = buffer_size
        self.PEER_LIST = {}  # Dictionary to track peers with their username and last seen timestamp
        self.PEER_TIMEOUT = peer_timeout
        self.connected_ips = {}  # Mapping of IPs to usernames
        self.running = True

    # Function to send broadcast presence messages
    def broadcast_presence(self, username):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)

        message = username.encode()  # Encode username to send in broadcast

        while self.running:
            try:
                # Send broadcast message with the username
                sock.sendto(message, (self.BROADCAST_IP, self.PORT))
                time.sleep(5)  # Send message every 5 seconds
            except Exception as e:
                print(f"Errore invio broadcast: {e}")
                break

    # Function to handle incoming messages and update peer list
    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.PORT))  # Listen on all network interfaces
        print(f"In ascolto su porta {self.PORT}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(self.BUFFER_SIZE)
                peer_ip = addr[0]
                username = data.decode()  # Decode incoming message to get username
                
                # Update or add the peer in the PEER_LIST
                self.PEER_LIST[peer_ip] = {'username': username, 'last_seen': time.time()}  # Set last seen time
                self.connected_ips[peer_ip] = username  # Map IP to username
                print(f"{username} connected from {peer_ip}. Number of connected peers: {len(self.PEER_LIST)}")
            except Exception as e:
                print(f"Errore ricezione: {e}")
                break

    # Function to update the peer list by removing inactive peers
    def update_peer_list(self):
        while self.running:
            time.sleep(1)  # Check the status of peers every second
            current_time = time.time()
            peers_to_remove = []
            
            # Iterate over PEER_LIST to check for inactive peers
            for peer, info in self.PEER_LIST.items():
                last_seen = info['last_seen']  # Access the last_seen timestamp correctly
                if current_time - last_seen > self.PEER_TIMEOUT:  # Peer inactive
                    peers_to_remove.append(peer)

            # Remove inactive peers
            for peer in peers_to_remove:
                del self.PEER_LIST[peer]
                del self.connected_ips[peer]  # Remove from connected IPs
                print(f"Peer {peer} disconnesso.")
                print(f"Numero di peer connessi: {len(self.PEER_LIST)}")

    # Function to start the peer network
    def start(self, username):
        self.running = True
        # Thread for broadcasting presence
        broadcast_thread = threading.Thread(target=self.broadcast_presence, args=(username,))
        broadcast_thread.daemon = True
        broadcast_thread.start()

        # Thread to listen for peers
        listen_thread = threading.Thread(target=self.listen_for_peers)
        listen_thread.daemon = True
        listen_thread.start()

        # Thread to monitor peer status
        peer_monitor_thread = threading.Thread(target=self.update_peer_list)
        peer_monitor_thread.daemon = True
        peer_monitor_thread.start()

    # Function to stop the network
    def stop(self):
        self.running = False
        print("Chiusura della rete P2P...")

    # Function to get the connected IPs
    def get_connected_ips(self):
        return self.connected_ips  # Returns the dictionary of IPs and usernames

