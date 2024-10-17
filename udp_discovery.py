import socket
import threading
import time

# Funzione per ricevere messaggi di scoperta
def receive_discovery(local_ip, local_port):
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.bind((local_ip, local_port))
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    actual_ip, actual_port = discovery_socket.getsockname()
    print(f"Ascolto di messaggi di scoperta su {actual_ip}:{actual_port}...")
    while True:
        try:
            data, addr = discovery_socket.recvfrom(1024)
            print(f"Messaggio di scoperta da {addr}: {data.decode()}")
            response = f"Peer discovered: {actual_ip}:{actual_port}"
            discovery_socket.sendto(response.encode(), addr)
            print(f"Inviata risposta a {addr}")
        except Exception as e:
            print("Errore nella scoperta:", e)

# Funzione per inviare messaggi di scoperta
def send_discovery(broadcast_ip, broadcast_port):
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = "DISCOVER_PEERS"
    while True:
        discovery_socket.sendto(message.encode(), (broadcast_ip, broadcast_port))
        print(f"Inviato messaggio di scoperta a {broadcast_ip}:{broadcast_port}")
        time.sleep(5)

def start_discovery(local_ip, local_port):
    broadcast_ip = '192.168.1.255'  # Indirizzo di broadcast per la tua rete locale
    broadcast_port = 12347  # Porta per il messaggio di scoperta
    receive_thread = threading.Thread(target=receive_discovery, args=(local_ip, local_port))
    receive_thread.start()
    send_thread = threading.Thread(target=send_discovery, args=(broadcast_ip, broadcast_port))
    send_thread.start()

if __name__ == '__main__':
    local_ip = '0.0.0.0'
    local_port = 0
    start_discovery(local_ip, local_port)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arresto in corso...")
