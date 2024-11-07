#  Peer-to-Peer Chat Application

Questa applicazione è una piattaforma di messaggistica peer-to-peer su reti locali, progettata per consentire comunicazioni sicure tra utenti connessi alla stessa rete. La piattaforma supporta chat globali, private e di gruppo, utilizzando la crittografia RSA per garantire la privacy nelle chat private. Il backend è gestito tramite Flask, mentre l’interfaccia utente è sviluppata in PyQt5.

## Indice

- [Obiettivo del Progetto](#obiettivo-del-progetto)
- [Funzionalità Principali](#funzionalità-principali)
- [Tecnologie Utilizzate](#tecnologie-utilizzate)
- [Struttura del Codice](#struttura-del-codice)
- [Analisi dei File Principali](#analisi-dei-file-principali)
- [Architettura del Sistema](#architettura-del-sistema)
- [Sicurezza](#sicurezza)
- [Limitazioni e Miglioramenti](#limitazioni-e-miglioramenti)
- [Debug e Testing](#debug-e-testing)
- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)

---

## Obiettivo del Progetto

L’applicazione è stata creata per facilitare una comunicazione sicura tra utenti collegati alla stessa rete locale. Supporta tre modalità di chat principali:
- **Chat Globale**: visibile a tutti gli utenti connessi alla rete.
- **Chat di Gruppo**: conversazione non crittografata tra più utenti selezionati.
- **Chat Privata**: comunicazione sicura tra due utenti, protetta da crittografia RSA per la massima privacy.

L’obiettivo principale è quello di offrire uno strumento sicuro e facile da usare per la comunicazione privata o di gruppo, garantendo che i messaggi siano visibili solo ai destinatari previsti.

---

## Funzionalità Principali
- **Registrazione e Login**: Gli utenti possono registrarsi e autenticarsi utilizzando nome utente e password. La password è cifrata e memorizzata in modo sicuro.
- **Crittografia RSA**: Ogni utente ha una coppia di chiavi RSA (privata e pubblica) che vengono utilizzate per cifrare e decifrare i messaggi.
- **Messaggi Privati e di Gruppo**: Gli utenti possono inviare messaggi privati ad altri utenti o creare gruppi di chat.
- **Rete Peer-to-Peer**: Utilizza la tecnologia peer-to-peer per inviare e ricevere messaggi tra utenti, rendendo la comunicazione sicura e decentralizzata.

### Sicurezza e Crittografia
- **Crittografia RSA per Chat Private**: Tutti i messaggi inviati nelle chat private sono cifrati con RSA, garantendo che solo il destinatario possa leggere il contenuto. Ogni utente genera una coppia di chiavi RSA (pubblica e privata) al momento dell'iscrizione.
- **Gestione Sicura delle Chiavi**: La chiave pubblica di un utente è condivisa per cifrare i messaggi a lui destinati, mentre la chiave privata è mantenuta sicura per decifrare solo i messaggi ricevuti.
  
### Interfaccia Intuitiva
- **Interfaccia PyQt5**: Un'interfaccia grafica sviluppata in PyQt5 permette di gestire facilmente chat, visualizzare gli utenti connessi e inviare messaggi in tempo reale.
- **Chat in Tempo Reale**: L'interfaccia consente di ricevere aggiornamenti in tempo reale dei messaggi e dell'elenco degli utenti online, garantendo una comunicazione fluida.

### Gestione degli Utenti
- **Registrazione e Login**: Ogni utente può registrarsi o accedere tramite un sistema di autenticazione sicura, con password crittografate memorizzate nel database.
- **Lista Utenti Connessi**: Mostra in tempo reale gli utenti disponibili per iniziare chat private o di gruppo.

### Persistenza dei Dati
- **Database SQLite**: La piattaforma utilizza SQLite per memorizzare in modo persistente i dati di utenti e messaggi, garantendo che tutte le informazioni siano disponibili anche dopo il riavvio dell'applicazione.

### Comunicazione Peer-to-Peer
- **Rete Peer-to-Peer**: Utilizza un protocollo peer-to-peer per permettere la comunicazione diretta tra i dispositivi nella stessa rete locale, senza necessità di un server centrale.

---

## Tecnologie Utilizzate

- **Flask**: Per il backend e la gestione delle API.
- **PyQt5**: Per l'interfaccia grafica (GUI).
- **SQLite**: Database per la persistenza dei dati.
- **RSA**: Algoritmo di crittografia asimmetrica per garantire la sicurezza nelle chat private.
- **TCP/UDP**: Protocolli per la comunicazione peer-to-peer.

---

## Struttura del Codice

### Struttura dei File

| File               | Descrizione                                                                                             |
|--------------------|---------------------------------------------------------------------------------------------------------|
| `API.py`           | Server API in Flask per la gestione degli utenti e dei messaggi, con supporto per la crittografia RSA. |
| `chat_windows.py`  | Definisce le finestre di chat per le comunicazioni private e di gruppo.                                |
| `login_app.py`     | Gestisce la finestra di login e registrazione tramite PyQt5 e interazione con l'API.                   |
| `main.py`          | Entry point principale, avvia l'API e l'interfaccia utente.                                            |
| `message_app.py`   | Applicazione di messaggistica principale per la chat globale.                                          |
| `peernetwork.py`   | Gestisce il protocollo di comunicazione peer-to-peer.                                                  |
| `user_manager.py`  | Interagisce con l'API per registrazione, autenticazione e gestione delle chiavi.                       |
| `user_data.db`     | Database SQLite per memorizzare gli utenti e i messaggi.                                               |
| `requirements.txt` | Elenco delle dipendenze.                                                                               |

---

## Analisi dei File Principali

### `API.py`
Questo file implementa il server API con Flask per la gestione delle operazioni principali:
- **Rotte di gestione utenti**: `/register` e `/login` per registrare e autenticare gli utenti.
- **Gestione delle chiavi RSA**: `/get_public_key` e `/get_private_key` per ottenere le chiavi necessarie alle chat private.
- **Gestione messaggi**: `/save_message` e `/load_messages` per salvare e recuperare i messaggi dal database.

### `chat_windows.py`
Definisce le finestre PyQt5 per la chat:
- **Chat privata**: utilizza la chiave pubblica del destinatario per crittografare i messaggi.
- **Chat di gruppo**: invia messaggi non crittografati a più destinatari.
- Include un’interfaccia utente intuitiva per gestire la chat e visualizzare gli utenti connessi.

### `login_app.py`
Gestisce la finestra di login:
- Permette registrazione e login tramite chiamate all'API.
- Dopo l'autenticazione, l'utente viene indirizzato alla finestra di messaggistica principale.

### `main.py`
File di avvio principale:
- Esegue il server API come subprocess.
- Configura le variabili di rete e lancia l'interfaccia principale dell'applicazione.

### `message_app.py`
Componente principale dell'applicazione di messaggistica:
- Mostra la chat globale e la lista degli utenti connessi.
- Aggiorna automaticamente l’elenco degli utenti e i messaggi ricevuti.

### `peernetwork.py`
Modulo per la comunicazione peer-to-peer:
- Utilizza il broadcasting per rilevare e connettere i dispositivi in rete.
- Gestisce la trasmissione dei messaggi in chat private e di gruppo.

### `user_manager.py`
Gestisce le funzioni API per la registrazione e autenticazione utenti:
- Registra e autentica utenti tramite richieste API.
- Fornisce le chiavi RSA degli utenti per le chat private.

### `requirements.txt`
Include le principali dipendenze del progetto:
- **Flask** per il server API
- **PyQt5** per l'interfaccia grafica
- **cryptography** per la crittografia RSA
- **requests** per le comunicazioni HTTP tra applicazione e server API.

---

## Architettura del Sistema

L’architettura dell’applicazione è basata su una struttura modulare che separa la logica di rete (gestita da Flask e dal modulo peer-to-peer) dalla GUI (PyQt5). Le principali componenti dell’architettura sono:
1. **Backend (Flask)**: Un server API per la gestione della logica di autenticazione, crittografia e persistenza dei messaggi.
2. **Frontend (PyQt5)**: Un’interfaccia utente che facilita l’interazione e la gestione delle comunicazioni.
3. **Database (SQLite)**: Memorizza in modo persistente le informazioni sugli utenti e sui messaggi.
4. **Rete Peer-to-Peer**: Gestita dal modulo `peernetwork.py`, consente agli utenti di rilevare altri dispositivi sulla stessa rete locale e stabilire connessioni per comunicazioni sicure.

## Sicurezza

- **RSA per Chat Private**: La sicurezza delle chat private dipende dalla gestione delle chiavi RSA; assicurarsi che le chiavi private non siano accessibili da parte di altri.
- **Salvataggio sicuro delle password**: Le password sono cifrate con hashing (SHA-256) prima di essere memorizzate.

---

## Limitazioni e Implementazioni

### Limitazioni Correnti
- **Solo Rete Locale**: Questa applicazione funziona esclusivamente su reti locali, limitandone l’uso in contesti di rete più ampi.
- **Sicurezza dell'API**: Attualmente il server Flask è configurato per ambienti di sviluppo. In ambienti di produzione, si consiglia di adottare misure di sicurezza avanzate.
- **Scalabilità Limitata**: L'architettura peer-to-peer è più adatta per reti di piccole dimensioni, come LAN aziendali o domestiche.

### Implementazioni Future
- **Rete Ibrida**: Considerare l'implementazione di una rete ibrida per supportare la comunicazione su reti più grandi o distribuite.
- **Ottimizzazione della Crittografia**: Utilizzare chiavi simmetriche temporanee nelle chat di gruppo per migliorare la sicurezza senza appesantire il sistema.
- **Miglioramenti UI**: L'interfaccia potrebbe essere migliorata con nuove funzionalità, come notifiche di stato per i messaggi, una visualizzazione avanzata degli utenti e temi personalizzabili.

## Debug e Testing

1. **Debug del Server**:
   - Usare `Flask` in modalità di debug durante lo sviluppo per ricevere messaggi di errore dettagliati.

2. **Test dell'Interfaccia**:
   - La parte grafica può essere testata manualmente per verificare che tutte le funzionalità siano accessibili e funzionino correttamente.
   - Per test automatici, considerare l'uso di strumenti come Pytest e unittest per le funzionalità non-UI.

----

----

---

## Prerequisiti

Assicurati di avere installato quanto segue:

- *Python 3.10 o superiore*
- *pip*: Gestore di pacchetti per Python
- *Virtualenv* (consigliato): Per creare un ambiente virtuale

---

## Installazione

1. **Clona il repository**:

   Apri il terminale ed esegui il comando seguente per clonare il repository:

   ```bash
   git clone https://github.com/tua_repo/app_messaggistica.git
   cd app_messaggistica
   ```

2. **Installa le dipendenze**:

   Assicurati di avere `pip` installato. Installa tutte le dipendenze richieste eseguendo:

   ```bash
   pip install -r requirements.txt
   ```

## Avvio del Programma

1. **Avvia il server Flask**:

   Esegui il server API per gestire il backend dell'applicazione:

   ```bash
   python API.py
   ```

   Una volta avviato, il server sarà accessibile all'indirizzo [http://<ip_server>:5003]. <br>
   Sostituisci `<ip_server>` con l'indirizzo IP locale del server, se necessario. 
   Sostituisci l'URL generato dall'API nei file `user_manager.py` e `chat_windows` per garantire la corretta comunicazione tra i moduli.
   Sostituisci indirizzo IP brodcast del tuo computer nel file `peernetwork.py` per garantire la corretta comunicazione tra i dispositivi.
   <br> <br>

2. **Avvia l'interfaccia grafica**: <br>
   **Dopo aver eseguito tutte le sostituizioni precedenti nei vari file allora:**<br>
   Esegui il file principale per aprire l'interfaccia grafica dell'applicazione:

   ```bash
   python main.py
   ```

   Verrà aperta una finestra in cui potrai utilizzare le funzionalità dell'applicazione, inclusa la chat globale, le chat private e le chat di gruppo. <br> <br>

3. **Registrazione e Accesso**:
   - Crea un nuovo account per iniziare a utilizzare l'applicazione.
   - Accedi con le credenziali create per accedere alla chat principale.


