import socket
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

# La classe PeerNetwork rappresenta una rete di peer in un sistema di comunicazione
# Peer (ovvero i nodi della rete) si connettono tra loro per inviare e ricevere messaggi
class PeerNetwork(QObject):
    # Signal per comunicare un messaggio ricevuto all'interfaccia utente
    message_received_signal = pyqtSignal(str)  # Segnale emesso quando viene ricevuto un nuovo messaggio

    # Inizializzazione della classe PeerNetwork
    def __init__(self, broadcast_ip="172.20.10.15", port=5000, buffer_size=1024, peer_timeout=10):
        super().__init__()  # Necessario per l'inizializzazione di QObject (PyQt)
        self.BROADCAST_IP = broadcast_ip  # Indirizzo IP di broadcast per inviare messaggi
        self.PORT = port  # Porta su cui il peer ascolterà
        self.BUFFER_SIZE = buffer_size  # Dimensione massima del buffer per ricevere i dati
        self.PEER_LIST = {}  # Dizionario per tenere traccia dei peer con il nome utente e il timestamp dell'ultima attività
        self.PEER_TIMEOUT = peer_timeout  # Tempo di inattività dopo il quale un peer viene considerato disconnesso
        self.connected_ips = {}  # Dizionario che mappa gli indirizzi IP agli username dei peer connessi
        self.running = True  # Flag per mantenere attiva la rete peer-to-peer

    # Funzione per broadcastare la propria presenza sulla rete (invio del nome utente via UDP)
    def broadcast_presence(self, username):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Imposta il socket per il broadcast
        sock.settimeout(0.2)  # Timeout per evitare che il socket blocchi troppo a lungo

        message = username.encode()  # Codifica il nome utente per inviarlo nel messaggio di broadcast

        while self.running:
            try:
                # Invia il messaggio di broadcast con il nome utente sulla rete
                sock.sendto(message, (self.BROADCAST_IP, self.PORT))
                time.sleep(5)  # Aspetta 5 secondi prima di inviare un altro broadcast
            except Exception as e:
                print(f"Errore durante il broadcast: {e}")
                break  # Se si verifica un errore, interrompe il ciclo

    # Funzione per ascoltare i messaggi ricevuti da altri peer sulla rete
    def listen_for_peers(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", self.PORT))  # Ascolta su tutte le interfacce di rete sulla porta definita
        print(f"Ascoltando sulla porta {self.PORT}...")

        while self.running:
            try:
                data, addr = sock.recvfrom(self.BUFFER_SIZE)  # Riceve un messaggio da un peer
                peer_ip = addr[0]  # Estrae l'indirizzo IP del peer
                username = data.decode()  # Decodifica il messaggio per ottenere il nome utente

                # Aggiunge o aggiorna il peer nella lista dei peer
                self.PEER_LIST[peer_ip] = {'username': username, 'last_seen': time.time()}  # Aggiunge il timestamp dell'ultima attività
                self.connected_ips[peer_ip] = username  # Mappa l'IP al nome utente
                print(f"{username} si è connesso da {peer_ip}. Peers connessi: {len(self.PEER_LIST)}")
            except Exception as e:
                print(f"Errore durante la ricezione: {e}")
                break  # Interrompe in caso di errore

    # Funzione per monitorare lo stato dei peer e rimuovere quelli inattivi
    def update_peer_list(self):
        while self.running:
            time.sleep(1)  # Controlla lo stato ogni secondo
            current_time = time.time()  # Ottiene il timestamp corrente
            peers_to_remove = []  # Lista di peer da rimuovere

            # Verifica se i peer sono inattivi (superano il timeout definito)
            for peer, info in self.PEER_LIST.items():
                last_seen = info['last_seen']  # Ultimo timestamp di attività del peer
                if current_time - last_seen > self.PEER_TIMEOUT:  # Se il peer è inattivo
                    peers_to_remove.append(peer)

            # Rimuove i peer inattivi dalla lista
            for peer in peers_to_remove:
                del self.PEER_LIST[peer]
                del self.connected_ips[peer]  # Rimuove anche dalla lista degli IP connessi
                print(f"Peer {peer} disconnesso. Peers connessi: {len(self.PEER_LIST)}")

    # Funzione per avviare la rete peer-to-peer
    def start(self, username):
        self.running = True
        # Thread per il broadcast della propria presenza sulla rete
        broadcast_thread = threading.Thread(target=self.broadcast_presence, args=(username,))
        broadcast_thread.daemon = True  # Imposta il thread come "demone" per terminare automaticamente alla chiusura del programma
        broadcast_thread.start()

        # Thread per ascoltare i peer sulla rete
        listen_thread = threading.Thread(target=self.listen_for_peers)
        listen_thread.daemon = True
        listen_thread.start()

        # Thread per monitorare lo stato dei peer
        peer_monitor_thread = threading.Thread(target=self.update_peer_list)
        peer_monitor_thread.daemon = True
        peer_monitor_thread.start()

    # Funzione per fermare la rete peer-to-peer
    def stop(self):
        self.running = False
        print("Arresto della rete P2P...")

    # Funzione per ottenere l'IP di un peer a partire dal suo nome utente
    def get_ip_by_username(self, username):
        """Restituisce l'indirizzo IP associato al nome utente."""
        for ip, user in self.connected_ips.items():
            if user == username:
                return ip
        return None  # Restituisce None se l'utente non è trovato

    # Funzione per ottenere l'elenco degli IP connessi
    def get_connected_ips(self):
        return self.connected_ips  # Restituisce il dizionario degli IP connessi e dei rispettivi nomi utente

    # Funzione che avvia un server TCP per ricevere messaggi da un altro peer
    def start_peer_server(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", port))  # Ascolta su tutte le interfacce di rete
        server_socket.listen(5)  # Imposta il numero massimo di connessioni in coda
        print(f"Ascoltando sulla porta {port}...")

        while True:
            client_socket, addr = server_socket.accept()  # Accetta una connessione in ingresso
            print(f"Connessione stabilita con {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()  # Avvia un thread per gestire la connessione

    # Funzione per gestire un client che invia un messaggio
    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')  # Riceve il messaggio
                if not message:  # Se il messaggio è vuoto, termina la connessione
                    break
                print(f"Messaggio ricevuto: {message}")
                if message.startswith("CHAT_CLOSED|"):  # Se il messaggio riguarda la chiusura di una chat
                    chat_id = message.split("|", 1)[1]
                    print(f"La chat {chat_id} è stata chiusa e sarà contrassegnata come inattiva.")
                elif message.startswith("DISCONNECT|"):  # Se il messaggio riguarda la disconnessione di un peer
                    chat_id = message.split("|", 1)[1]
                    print(f"La chat {chat_id} è stata chiusa dal peer.")

                # Emesso il segnale per aggiornare l'interfaccia utente con il nuovo messaggio
                self.message_received_signal.emit(message)
        except Exception as e:
            print(f"Errore durante la ricezione del messaggio: {e}")
        finally:
            client_socket.close()  # Chiude la connessione

    # Funzione per inviare un messaggio a un altro peer tramite TCP
    def send_message(self, peer_ip, peer_port, message):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip, peer_port))  # Connessione al peer
            client_socket.sendall(message.encode('utf-8'))  # Invia il messaggio codificato
        except Exception as e:
            print(f"Errore durante l'invio del messaggio: {e}")
        finally:
            client_socket.close()  # Chiude la connessione

    # Funzione per inviare una notifica che una chat è stata chiusa
    def send_chat_closed_notification(self, chat_id):
        """Invia una notifica indicando che una chat specifica è stata chiusa."""
        message = f"CHAT_CLOSED|{chat_id}"
        for ip, _ in self.connected_ips.items():
            self.send_message(ip, 5001, message)  # Invia il messaggio a tutti i peer connessi

    # Funzione per inviare una notifica che una connessione è stata chiusa
    def send_disconnection_notification(self, chat_id):
        """Invia un messaggio per indicare che una finestra di chat è stata chiusa."""
        message = f"DISCONNECT|{chat_id}"
        for ip, _ in self.connected_ips.items():
            self.send_message(ip, 5001, message)  # Invia il messaggio a tutti i peer connessi
