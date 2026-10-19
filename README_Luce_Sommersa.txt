LUCE SOMMERSA — VERSIONE 4
==========================

Avventura narrativa in pixel art: 31 ambienti in 10 capitoli. La ricerca di Neri sembra portare verso una persona che ti sta aspettando; soltanto nell'ultima stanza si capisce cosa rappresentavano davvero gli ostacoli lungo il viaggio.

QUATTRO BOSS, NON DIECI
-----------------------
1. IL PORTIERE — ti dice che non sei degno di raggiungere Neri e ti rimanda indietro.
2. IL GUARDIANO — nega che lei ti stia aspettando e minaccia di respingerti.
3. IL MERCANTE — offre scorciatoie, promesse e finali alternativi in cambio di un patto.
4. LA SENTINELLA — cerca di convincerti che Neri non voglia vederti e che non meriti di arrivare.

Questi sono gli unici quattro boss veri. Gli altri ambienti mantengono il numero originale di stanze, ma usano percorsi, sequenze, stealth e prove narrative invece di ripetere combattimenti.

INCONTRO FINALE SPECIALE
------------------------
L'ultimo incontro non è un quinto boss tradizionale. Non puoi attaccare la figura: devi lasciare che il frammento di memoria ti raggiunga. Ogni impatto la indebolisce. La regola cambia proprio quando il gioco ti ha abituato a schivare tutto.

Solo qui la storia rivela che i quattro avversari erano difese interiori: Negazione, Rabbia, Contrattazione e Depressione. Prima di questo momento sono presentati come figure che ti separano da Neri, che credi ti stia aspettando.

COMBATTIMENTO
-------------
• Il tuo turno: premi E, Z, Invio o Spazio quando il cursore è vicino al centro della barra. Il tempismo determina il danno.
• Il turno nemico: muovi il cuore con WASD o frecce e usa Shift per uno scatto.
• I boss hanno più fasi e schemi che diventano più veloci e densi man mano che la loro salute diminuisce.
• L'attacco a strisce verticali è stato sostituito da un'onda orizzontale con una fascia sicura annunciata in anticipo.
• Se finisce il Respiro durante un boss, lo scontro riparte dall'inizio.

IL CORRIDOIO DEL POSTO VUOTO
---------------------------
Elia è stato rimosso. Il percorso si attraversa in autonomia: nessuna scorta da seguire e nessun compagno che possa bloccare il progresso.

LA DEVIAZIONE DEL TRENO: TROVA LA CHIAVE
---------------------------------------
Dopo aver completato l'inseguimento del Capocorsa, torna nella carrozza principale e interagisci con la porta laterale illuminata.

1. Nella CARROZZA BAGAGLI, esamina il Registro di carico: contiene il riferimento S-17.
2. Segui l'uscita per entrare nella CABINA S-17.
3. Esamina il Cassetto di emergenza e recupera la chiave d'ottone.
4. Torna alla carrozza principale: con la chiave puoi superare la soglia verso la torre.

INSTALLAZIONE SU UBUNTU / LINUX
-------------------------------
1. Estrai lo ZIP in una cartella nuova. Mantieni insieme tutti i file, compresa la cartella luce_sommersa_assets e il file luce_sommersa_engine.py.
2. Installa Pygame, se non è già presente:

   sudo apt update
   sudo apt install python3-pygame

3. Apri un terminale nella cartella estratta e avvia:

   chmod +x avvia_gioco.sh
   ./avvia_gioco.sh

In alternativa: python3 luce_sommersa.py

COMANDI
-------
WASD o frecce: movimento nell'ambiente e schivata durante il turno nemico
SHIFT: scatto più veloce durante la schivata
E / Z / INVIO / SPAZIO: interagisci, avanza i dialoghi o attacca durante il tuo turno
1 / 2 / 3: scelte nei dialoghi
M: audio
ESC: esci

COLLAUDO
--------
Il codice supera la compilazione sintattica. Ho verificato la presenza di 31 ambienti, quattro scene boss, l'assenza di riferimenti a Elia e la logica del combattimento speciale. Pygame non è installato in questo ambiente, quindi non ho potuto verificare il gioco in una finestra grafica: il bilanciamento e la leggibilità vanno confermati con una partita reale su Ubuntu.


AGGIORNAMENTO NARRATIVO v5
- I quattro boss restano figure misteriose durante tutta la ricerca di Neri.
- Solo dopo l'incontro speciale finale, le quattro figure ritornano e spiegano in prima persona che cosa rappresentavano: Negazione, Rabbia, Contrattazione e Depressione.
- Accettazione non e un quinto boss: e la comprensione finale, non un nemico da sconfiggere.
- Il gioco conserva i suoi 31 ambienti.
