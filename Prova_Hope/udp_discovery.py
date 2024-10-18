import socket
import threading
import time

class PeerNetwork:
    def __init__(self, broadcast_ip="192.168.178.255", port=5000, buffer_size=1024, peer_timeout=10):
        self.BROADCAST_IP = broadcast_ip
        self.PORT = port
        self.BUFFER_SIZE = buffer_size
        self.PEER_LIST = {}  # Dizionario che terrà traccia degli altri peer e del loro timestamp
        self.PEER_TIMEOUT = peer_timeout  # Timeout in secondi per considerare un peer disconnesso
        self.connected_ips = []  # Lista degli IP connessi in continuo aggiornamento
        self.running = True

    # Funzione per inviare messaggi in broadcast
    def broadcast_presence(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.2)

        message = b""

        while self.running:
            try:
                # Invia messaggio in broadcast (vuoto, non serve stamparlo)
                sock.sendto(message, (self.BROADCAST_IP, self.PORT))
                time.sleep(5)  # Invia messaggio ogni 5 secondi
            except Exception as e:
                print(f"Errore invio broadcast: {e}")
                break

    # Funzione per gestire l'aggiornamento dei peer connessi
    def update_peer_list(self):
        while self.running:
            time.sleep(1)  # Controlla lo stato dei peer ogni secondo
            current_time = time.time()
            peers_to_remove = []
            
            for peer, last_seen in self.PEER_LIST.items():
                if current_time - last_seen > self.PEER_TIMEOUT:  # Peer inattivo
                    peers_to_remove.append(peer)

            # Rimuovi i peer inattivi e aggiorna la lista
            for peer in peers_to_remove:
                del self.PEER_LIST[peer]
                if peer in self.connected_ips:
                    self.connected_ips.remove(peer)  # Rimuovi dalla lista degli IP connessi
                print(f"Peer {peer} disconnesso.")
                print(f"Numero di peer connessi: {len(self.PEER_LIST)}")

    # Funzione per ricevere i messaggi dagli altri peer
    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.PORT))  # Ascolta su tutte le interfacce di rete
        print(f"In ascolto su porta {self.PORT}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(self.BUFFER_SIZE)
                peer_ip = addr[0]
                
                if peer_ip not in self.PEER_LIST:  # Nuovo peer rilevato
                    self.PEER_LIST[peer_ip] = time.time()  # Registra il tempo di ricezione
                    self.connected_ips.append(peer_ip)  # Aggiungi alla lista degli IP connessi
                    print(f"Numero di peer connessi: {len(self.PEER_LIST)}")
                else:
                    # Aggiorna il timestamp del peer esistente
                    self.PEER_LIST[peer_ip] = time.time()
            except Exception as e:
                print(f"Errore ricezione: {e}")
                break

    # Funzione per avviare i thread e gestire la rete peer-to-peer
    def start(self):
        self.running = True
        # Thread per inviare il messaggio di presenza
        broadcast_thread = threading.Thread(target=self.broadcast_presence)
        broadcast_thread.daemon = True
        broadcast_thread.start()

        # Thread per ascoltare i messaggi in arrivo dagli altri peer
        listen_thread = threading.Thread(target=self.listen_for_peers)
        listen_thread.daemon = True
        listen_thread.start()

        # Thread per monitorare lo stato dei peer e rimuovere quelli inattivi
        peer_monitor_thread = threading.Thread(target=self.update_peer_list)
        peer_monitor_thread.daemon = True
        peer_monitor_thread.start()

    # Funzione per fermare il network e i suoi thread
    def stop(self):
        self.running = False
        print("Chiusura della rete P2P...")

    # Funzione per ottenere la lista aggiornata degli IP connessi
    def get_connected_ips(self):
        return self.connected_ips

# Esempio di utilizzo della classe
if __name__ == "__main__":
    peer_network = PeerNetwork()
    peer_network.start()

    try:
        while True:
            time.sleep(1)
            # Stampa la lista aggiornata degli IP connessi
            print(f"Dispositivi connessi: {peer_network.get_connected_ips()}")
    except KeyboardInterrupt:
        peer_network.stop()
