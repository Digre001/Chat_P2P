import socket
import threading
import time

# Configurazione
BROADCAST_IP = "127.0.0.1"  # Indirizzo broadcast
PORT = 5000  # Porta UDP usata per la comunicazione
BUFFER_SIZE = 1024
PEER_LIST = set()  # Insieme che terrà traccia degli altri peer

# Funzione per inviare messaggi in broadcast
def broadcast_presence():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(0.2)

    message = b"Hello from peer"

    while True:
        try:
            # Invia messaggio in broadcast
            sock.sendto(message, (BROADCAST_IP, PORT))
            time.sleep(5)  # Invia messaggio ogni 5 secondi
        except Exception as e:
            print(f"Errore invio broadcast: {e}")
            break

# Funzione per ricevere i messaggi dagli altri peer
def listen_for_peers():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))  # Ascolta su tutte le interfacce di rete
    print(f"In ascolto su porta {PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if addr[0] not in PEER_LIST:  # Se il peer non è ancora nella lista
                PEER_LIST.add(addr[0])
                print(f"Nuovo peer rilevato: {addr[0]} - Messaggio: {data.decode()}")
            else:
                print(f"Messaggio ricevuto da {addr[0]}: {data.decode()}")
        except Exception as e:
            print(f"Errore ricezione: {e}")
            break

# Avvia il thread per l'invio e la ricezione
if __name__ == "__main__":
    # Thread per inviare il messaggio di presenza
    broadcast_thread = threading.Thread(target=broadcast_presence)
    broadcast_thread.daemon = True
    broadcast_thread.start()

    # Thread per ascoltare i messaggi in arrivo dagli altri peer
    listen_thread = threading.Thread(target=listen_for_peers)
    listen_thread.daemon = True
    listen_thread.start()

    # Mantieni il programma in esecuzione
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Chiusura programma")
            break
