import socket
import threading
import time

# Funzione per ricevere messaggi di scoperta
def receive_discovery(local_ip, local_port):
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.bind((local_ip, local_port))
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"Listening for discovery messages on {local_ip}:{local_port}...") # non sono sicuro serva penso si possa cancellare
    while True:
        try:
            data, addr = discovery_socket.recvfrom(1024)
            print(f"Discovery message from {addr}: {data.decode()}") # non so se srve anche questo print penso si possa cancellare
            # Rispondere con il proprio indirizzo IP e porta
            response = f"Peer discovered: {local_ip}:{local_port}"
            discovery_socket.sendto(response.encode(), addr)
        except Exception as e:
            print("Error in discovery:", e)

# Funzione per inviare messaggi di scoperta
def send_discovery(broadcast_ip, broadcast_port):
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = "DISCOVER_PEERS"

    while True:
        discovery_socket.sendto(message.encode(), (broadcast_ip, broadcast_port))
        time.sleep(5)  # Invia il messaggio di broadcast ogni 5 secondi

