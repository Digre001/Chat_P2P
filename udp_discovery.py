import socket
import threading
import time

# Configurazione
BROADCAST_IP = "192.168.111.255"  # Indirizzo broadcast
PORT = 5000  # Porta UDP usata per la comunicazione
BUFFER_SIZE = 1024
PEER_LIST = {}  # Dizionario che terrà traccia degli altri peer e del loro timestamp
PEER_TIMEOUT = 10  # Timeout in secondi per considerare un peer disconnesso

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

# Funzione per gestire l'aggiornamento dei peer connessi
def update_peer_list():
    while True:
        time.sleep(1)  # Controlla lo stato dei peer ogni secondo
        current_time = time.time()
        peers_to_remove = []
        
        for peer, last_seen in PEER_LIST.items():
            if current_time - last_seen > PEER_TIMEOUT:  # Peer inattivo
                peers_to_remove.append(peer)

        # Rimuovi i peer inattivi e aggiorna la lista
        for peer in peers_to_remove:
            del PEER_LIST[peer]
            print(f"Peer {peer} disconnesso.")
            print(f"Numero di peer connessi: {len(PEER_LIST)}")

# Funzione per ricevere i messaggi dagli altri peer
def listen_for_peers():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PORT))  # Ascolta su tutte le interfacce di rete
    print(f"In ascolto su porta {PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            peer_ip = addr[0]
            
            if peer_ip not in PEER_LIST:  # Nuovo peer rilevato
                print(f"Nuovo peer rilevato: {peer_ip}")
                PEER_LIST[peer_ip] = time.time()  # Registra il tempo di ricezione
                print(f"Numero di peer connessi: {len(PEER_LIST)}")
            else:
                # Aggiorna il timestamp del peer esistente
                PEER_LIST[peer_ip] = time.time()
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

    # Thread per monitorare lo stato dei peer e rimuovere quelli inattivi
    peer_monitor_thread = threading.Thread(target=update_peer_list)
    peer_monitor_thread.daemon = True
    peer_monitor_thread.start()

    # Mantieni il programma in esecuzione
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Chiusura programma")
            break
