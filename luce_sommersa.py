#!/usr/bin/env python3
# LUCE SOMMERSA — campagna narrativa estesa.
# Uses the procedural pixel-art/audio engine from luce_sommersa.py.
import math
import random
import sys
from pathlib import Path
import pygame
from luce_sommersa_engine import Game, WIDTH, HEIGHT, TILE, PALETTES, draw_text, distance, clamp, Particle

# Each scene is a distinct connected space. Exits deliberately use all four sides.
def area(ch, title, style, floors, blocks, spawn, exit_dir, door, next_id, npc, npc_pos, task,
         intro, npc_lines, props=None, order=None, route=None, battle=None, options=None, palette=None, events=None):
    return {
        'chapter': ch, 'title': title, 'style': style,
        'floors': floors, 'blocks': blocks, 'spawn': spawn,
        'exit': exit_dir, 'door': door, 'next': next_id,
        'npc': npc, 'npc_pos': npc_pos, 'task': task,
        'intro': intro, 'npc_lines': npc_lines,
        'props': props or [], 'order': order or [], 'route': route or [], 'events': events or [],
        'battle': battle, 'options': options or [], 'palette': palette,
    }

STORY_AREAS = {
'platform': area(1, 'BINARIO ZERO', 'station',
    [(0,275,390,100),(155,170,160,160),(300,220,260,145),(525,275,435,100),(120,340,200,175)],
    [(170,300,66,26),(258,300,39,26),(190,380,60,25)], (65,320), 'right', (944,320), 'garden', 'PIP', (300,258), 'two_step',
    [('VOCE','Ti risvegli su una banchina che non appare su nessuna mappa.'),('VOCE','Non ricordi da quanto cammini. Ricordi soltanto il nome di Neri e la certezza ostinata che, se ti sbrighi, puoi ancora raggiungerla.'),('VOCE','Ogni porta che attraversi promette una traccia. Nessuna ti dice cosa succedera quando la troverai.'),('VOCE','Sotto il tabellone, una frase e stata graffiata con una chiave: NON CONFONDERE LA MANCANZA CON UNA COLPA.')],
    [('PIP','Finalmente. Da tre giorni la stazione continua a preparare un biglietto per una persona che non sa nominare.'),('PIP','Le tracce dicono che Neri e passata di qui. Se continui, forse la raggiungi.'),('PIP','C e una cosa strana: ogni volta che qualcuno ti indica una strada, sembra anche chiederti di non guardare troppo da vicino dove porta.'),('PIP','La porta non vuole una chiave. Vuole che tu guardi il tabellone senza chiedergli di raccontarti una bugia.')],
    props=[{'name':'Tabellone degli arrivi','pos':(270,430),'lines':[('TABELLONE','DESTINAZIONE: NON SCRITTA. RITORNO: NON GARANTITO.'),('VOCE','La grafia e tua. Non ricordi di averla scritta, ma la parola RITORNO ti fa stringere lo stomaco.')] }]),
'garden': area(1, 'GIARDINO DI VETRO', 'garden',
    [(0,278,275,90),(210,230,190,130),(345,125,270,175),(410,0,150,150),(520,230,230,130),(685,278,275,90),(410,340,150,160),(350,475,280,165)],
    [(242,250,34,20),(350,155,30,48),(580,155,30,48),(710,342,32,20)], (45,320), 'up', (480,10), 'node', 'NIA', (475,420), 'runes',
    [('VOCE','La citta sparisce dietro una parete di vetro. Qui le cose non si rompono: restano incrinate, aspettando che qualcuno le guardi.'),('VOCE','Ogni luce riflette un momento in cui avresti potuto dire qualcosa. Nessuna ti mostra cosa sarebbe successo dopo.')],
    [('NIA','Non sono tre oggetti da raccogliere. Sono tre passi da ricordare.'),('NIA','Azzurro: cio che sai. Oro: cio che temi. Rosa: cio che non hai detto.'),('NIA','Cammina sulle luci nell’ordine giusto. Non cercare di farle tacere.')],
    route=[(250,320),(480,195),(715,320)]),
'node': area(1, 'CAMERA DEL NODO', 'chamber',
    [(380,0,200,170),(265,130,430,145),(0,245,960,120),(330,350,300,290)],
    [(350,280,45,38),(565,280,45,38),(405,390,35,24),(520,390,35,24)], (480,585), 'down', (480,630), 'bells', 'IL PORTIERE', (480,300), 'battle',
    [('VOCE','Oltre il vetro, la stanza si stringe attorno ai tuoi passi.'),('VOCE','Una figura prende forma da tutti i cartelli che indicano ancora la strada per Neri.'),('IL PORTIERE','Neri ti aspetta dall’altra parte. Ma non tu. Torna indietro: non sei degno di arrivare fin lì. Cerca un’altra strada, se proprio non vuoi arrenderti.')],
    [('IL PORTIERE','Lei è lì che ti aspetta. Ma se ti vedesse adesso, capirebbe quanto sei indegno.'),('IL PORTIERE','Torna indietro. Trova un’altra prova, un’altra porta. Quando sarai abbastanza, forse ti lascerò passare.'),('IL PORTIERE','Vuoi raggiungerla? Allora dimostrami che puoi sopravvivere alla strada che ti separa da lei.')], battle='denial'),
'bells': area(2, 'LA CITTA DEI CAMPANELLI', 'bells',
    [(420,0,120,160),(320,130,330,130),(125,235,700,130),(0,285,230,85),(730,285,230,85),(230,350,190,160)],
    [(140,255,40,25),(240,255,40,25),(640,255,40,25),(715,255,35,25),(270,395,50,26)], (480,45), 'left', (10,320), 'tower', 'DADO', (480,300), 'sequence',
    [('VOCE','La citta e costruita attorno a una piazza, ma tutte le strade sembrano riportare allo stesso campanile.'),('VOCE','Gli abitanti non si sono dimenticati di te. Si sono dimenticati di quale versione di te hanno incontrato.')],
    [('DADO','I campanelli non suonano per chi arriva. Suonano per chi se ne va.'),('DADO','La melodia e stata spezzata dal giorno in cui qualcuno e partito. La sequenza corretta e secondo, primo, terzo.'),('DADO','Non devi raccoglierli. Devi farli rispondere.')],
    props=[{'name':'Campanello I','pos':(190,305),'lines':[('CAMPANELLO','Un suono breve. Ti torna in mente una risata interrotta da un fischio di treno.')]},{'name':'Campanello II','pos':(280,305),'lines':[('CAMPANELLO','Una nota piu bassa. Qualcuno diceva sempre che saresti arrivato in ritardo.')]},{'name':'Campanello III','pos':(680,305),'lines':[('CAMPANELLO','La terza nota non chiude la melodia. La lascia aperta, come una domanda.')] }], order=[1,0,2]),
'tower': area(2, 'LA SCALA CHE NON FINISCE', 'tower',
    [(745,270,215,100),(590,235,180,155),(430,180,180,180),(325,100,150,165),(380,0,145,112)],
    [(760,290,45,30),(640,255,44,30),(485,205,50,26),(375,120,55,26)], (920,320), 'up', (480,10), 'market', 'IL GUARDIANO', (485,280), 'battle',
    [('VOCE','La scala gira, ma non sale. Ogni gradino riporta a una frase che avresti voluto urlare.'),('VOCE','In cima c e una figura fatta di porte sbattute, parole trattenute e domande senza risposta.')],
    [('IL GUARDIANO','Non è vero che ti aspetta. E se anche fosse, non ti lascerei passare.'),('IL GUARDIANO','Vattene. Non farmi perdere la pazienza: non sai cosa succede quando mi arrabbio.'),('IL GUARDIANO','Vuoi passare? Prova. Ogni volta che ti avvicini, ti ricaccerò indietro.')], battle='anger'),
'market': area(3, 'IL MERCATO DELLE COSE PERDUTE', 'market',
    [(420,470,130,170),(300,350,360,190),(170,245,610,125),(260,110,430,160),(620,230,205,130),(745,260,215,100)],
    [(285,135,68,50),(385,135,68,50),(485,135,68,50),(645,260,48,32),(340,390,62,34),(540,390,62,34)], (480,590), 'right', (944,320), 'alley', 'ADA', (490,310), 'choice',
    [('VOCE','Il mercato vende oggetti che non sono stati persi: lettere mai spedite, scuse provate davanti allo specchio, promesse che nessuno ha chiesto.'),('VOCE','La merce piu costosa e una risposta alla domanda: “E se avessi fatto diversamente?”')],
    [('ADA','Per comprare qualcosa devi lasciare qualcosa. Ma il ricordo piu caro non e quello che vuoi tenere: e quello che ti ostini a pagare.'),('ADA','Che cosa vuoi scambiare? La verita, il rimorso, oppure la possibilita di non pensarci?')],
    props=[{'name':'La bancarella vuota','pos':(320,300),'lines':[('ADA','Questa bancarella era piena di futuri possibili. La gente li compra quando non riesce a sopportare il presente.')] }],
    options=[('LA VERITA','Ammetti che non sapevi cosa dire.'),('IL RIMORSO','Ti prendi tutta la colpa, anche quella che non ti spetta.'),('LA FUGA','Cerchi un ricordo in cui non ti importava.')]),
'alley': area(3, 'IL VICOLO DELLE VETRINE', 'mirror',
    [(0,280,300,90),(220,235,210,140),(390,185,240,165),(565,250,395,120),(420,340,170,300)],
    [(255,260,38,42),(330,250,32,52),(610,275,32,46),(670,275,32,46)], (40,320), 'down', (500,630), 'library', 'IL MERCANTE', (495,420), 'battle',
    [('VOCE','Le vetrine mostrano tutte le versioni in cui hai detto la cosa giusta, al momento giusto.'),('VOCE','Ogni riflesso ti offre un patto. Basta una parola diversa e il treno puo tornare indietro.')],
    [('IL MERCANTE','Posso darti una strada più corta. Un saluto migliore. Una frase che ti farà sembrare diverso ai suoi occhi.'),('IL MERCANTE','E se fossi andato prima? E se le avessi detto che avevi paura? E se provassi ancora una volta?'),('IL MERCANTE','Ti darò tutto questo, se mi dimostri che vuoi davvero arrivare da lei. Ma ogni patto ha un prezzo.')], battle='bargaining'),
'library': area(4, 'BIBLIOTECA DELLE FRASI NON DETTE', 'library',
    [(410,0,150,165),(280,130,400,120),(150,220,660,110),(220,320,160,250),(600,320,150,250),(370,310,230,170),(780,280,180,100)],
    [(240,238,28,64),(280,238,28,64),(320,238,28,64),(630,238,28,64),(670,238,28,64),(710,238,28,64),(410,355,35,25),(515,355,35,25)], (480,45), 'right', (944,320), 'pages', 'LUMA', (480,300), 'choice',
    [('VOCE','Gli scaffali arrivano oltre il soffitto. Le frasi che non hai detto occupano piu spazio di quelle che hai pronunciato.'),('VOCE','Alcune sono diventate cosi lunghe che nessuno ricorda piu come cominciavano.')],
    [('LUMA','Ogni frase qui ha due versioni: quella che avresti voluto dire e quella che ti sei raccontato dopo.'),('LUMA','Completa questa frase senza cercare di renderla perfetta: “Non te l’ho detto perche...”'),('LUMA','Scegli la risposta che ti somiglia di piu. La biblioteca accettera anche una frase incompleta.')],
    options=[('AVEVO PAURA','“Avevo paura che, se ti salutavo davvero, ti avrei persa.”'),('NON VOLEVO FERIRTI','“Non volevo chiederti di restare, perche non volevo essere egoista.”'),('NON LO SO ANCORA','“Non ho capito tutto neanche adesso. Ma smetto di fingere che non mi importasse.”')]),
'pages': area(4, 'LA SALA DELLE FRASI PERFETTE', 'paper',
    [(0,280,270,100),(215,225,250,140),(405,170,180,165),(560,225,240,140),(750,285,210,90),(410,320,180,320)],
    [(250,245,28,52),(295,245,28,52),(640,245,28,52),(685,245,28,52),(440,400,35,25),(520,400,35,25)], (480,585), 'down', (480,630), 'waiting', 'LA SENTINELLA', (480,300), 'battle',
    [('VOCE','Le frasi corrette sono appese come quadri, ma ormai non riesci neanche a leggerle.'),('VOCE','La stanza non ti promette piu una soluzione. Non c e una porta segreta, nessun messaggio da trovare. Solo stanchezza.')],
    [('LA SENTINELLA','Lei non vuole vederti. Non ti meriti di arrivare fin qui.'),('LA SENTINELLA','Hai attraversato tutto questo per cosa? Per farti guardare e scoprire che non sei abbastanza?'),('LA SENTINELLA','Resta qui. Almeno qui non devi sentire la risposta.')], battle='depression'),
'waiting': area(5, 'SALA D’ATTESA', 'hospital',
    [(400,0,160,155),(270,120,420,130),(110,220,760,100),(0,270,220,90),(730,300,190,160),(600,400,180,120)],
    [(140,240,74,28),(255,240,74,28),(655,240,74,28),(765,330,70,28),(640,430,65,28)], (480,45), 'left', (10,320), 'room', 'IL PENDOLO', (480,300), 'rhythm',
    [('VOCE','La sala d’attesa e piena di sedie. Su ogni sedia siede una versione diversa di te, ancora in attesa di una risposta.'),('VOCE','Un orologio senza lancette batte il tempo con un suono leggermente fuori ritmo.')],
    [('IL PENDOLO','L attesa puo diventare un luogo in cui vivere, se lasci che ogni secondo chieda il permesso al successivo.'),('IL PENDOLO','Non devi fermare il tempo. Devi smettere di chiedergli di tornare indietro. Premi E quando il cerchio si accende: tre battiti.')]),
'room': area(5, 'LA STANZA DEL POSTO VUOTO', 'hospitalroom',
    [(750,280,210,100),(610,225,190,145),(430,190,220,130),(250,225,190,145),(0,280,300,100),(360,300,240,340),(360,0,240,230)],
    [(280,250,70,32),(610,250,70,32),(400,420,55,28),(505,420,55,28)], (920,320), 'up', (480,10), 'lobby', 'LA SEDIA VUOTA', (480,180), 'memory_walk',
    [('VOCE','Il letto e rifatto. Sul comodino c’e un bicchiere d’acqua pieno, anche se nessuno lo beve.'),('VOCE','Non c’e una persona da seguire. Ci sono tre dettagli rimasti qui dopo che tutti gli altri se ne sono andati.')],
    [('LA SEDIA VUOTA','Non sono Neri. Sono lo spazio che hai continuato a tenere libero per lei, anche quando la vita era gia andata avanti.'),('LA SEDIA VUOTA','Attraversa la stanza. Non devi portarmi da nessuna parte: devi guardare cio che e rimasto.')], route=[(480,520),(310,310),(480,145)]),
'lobby': area(6, 'IL RETRO DEL TEATRO', 'theatre',
    [(400,470,160,170),(280,350,400,150),(175,240,610,125),(300,110,360,160),(420,0,120,130),(0,280,220,90),(740,280,220,90)],
    [(320,380,58,35),(410,380,58,35),(500,380,58,35),(390,150,45,55),(520,150,45,55)], (480,590), 'up', (480,10), 'stage', 'LA CAPOCOMICA', (480,300), 'choice',
    [('VOCE','Dietro il sipario, tre costumi aspettano su tre sedie. La platea e vuota, ma senti un applauso quando entri.'),('VOCE','Per anni hai interpretato qualcuno che non aveva bisogno di niente. Il pubblico non ha mai chiesto il bis; eri tu a ripetere la scena.')],
    [('CAPOCOMICA','Scegli una maschera, ma non confonderla con il volto.'),('CAPOCOMICA','Puoi chiedere aiuto, accusare qualcuno, o far finta che non ti importasse. In scena funzionano tutte e tre. Fuori scena, no.')],
    options=[('CHIEDERE AIUTO','Ammetti che non riuscivi a farcela da solo.'),('ACCUSARE','Dai alla rabbia una frase e un bersaglio.'),('FINGERE','Dici che non ti importava e mantieni la maschera.')]),
'stage': area(6, 'IL PALCO SENZA PUBBLICO', 'stage',
    [(0,280,250,90),(200,240,560,190),(740,280,220,90),(320,110,320,180),(400,420,160,220)],
    [(290,285,40,24),(360,285,40,24),(430,285,40,24),(500,285,40,24),(570,285,40,24),(400,450,35,25),(525,450,35,25)], (480,590), 'right', (944,320), 'shore', 'IL SUGGERITORE', (480,205), 'route',
    [('VOCE','Le luci si accendono tutte insieme. Nessun pubblico. Nessun applauso. Solo il rumore del tuo fiato amplificato.'),('VOCE','La rabbia arriva in scena senza conoscere il testo. Ma sa tutte le battute che non hai mai pronunciato.')],
    [('LA RABBIA','Non serve combattere con me. Attraversa il palco: ogni luce è una frase che non hai mai detto.'),('LA RABBIA','Non devi recitare bene. Devi soltanto arrivare dall’altra parte senza tornare alla battuta di sempre.')], route=[(250,320),(480,190),(700,320),(480,440)]),
'shore': area(7, 'LA RIVA CHE SI MUOVE', 'lake',
    [(0,285,330,100),(240,220,220,140),(430,260,300,130),(600,330,150,200),(430,360,150,130),(400,430,180,210),(330,570,220,70)],
    [(90,300,48,26),(265,250,32,25),(485,285,35,25),(680,410,30,25),(450,475,34,24)], (40,320), 'down', (480,630), 'mirrorlake', 'IL BARCAIOLO', (500,390), 'route',
    [('VOCE','Per attraversare il lago devi camminare dove la superficie decide di sostenerti.'),('VOCE','Le pietre appaiono una alla volta, non davanti a te ma nella direzione in cui stai andando.')],
    [('BARCAIOLO','Non c’e una strada sicura per chi vuole sapere in anticipo dove arrivera.'),('BARCAIOLO','Segui i riflessi che si accendono: passerella, canneto, isola, riva. Se sbagli, l’acqua ti riporta all’ultimo punto sicuro.')],
    route=[(270,295),(465,285),(650,365),(480,500)]),
'mirrorlake': area(7, 'IL LAGO CHE TI GUARDA', 'mirrorlake',
    [(410,0,150,180),(300,140,360,150),(200,240,560,130),(0,280,270,95),(650,340,170,160),(400,350,150,290)],
    [(340,250,35,24),(590,250,35,24),(425,420,28,35),(495,420,28,35)], (480,45), 'left', (10,320), 'hall', 'IL BARCAIOLO', (480,300), 'tidal',
    [('VOCE','L’acqua riflette una vita in cui hai parlato al momento giusto. Poi l’immagine cambia: anche in quella vita, nessuno poteva promettere come sarebbe finita.'),('VOCE','Per la prima volta, il tuo riflesso non ti guarda indietro. Ti guarda avanti.')],
    [('IL BARCAIOLO','Le luci sulla superficie appaiono e scompaiono. Aspetta che l’acqua si ritiri, poi attraversa.'),('IL BARCAIOLO','Non devi vincere contro il lago. Devi imparare quando fare il prossimo passo.')], route=[(340,285),(590,285),(480,430)]),
'hall': area(8, 'LA CASA SENZA PORTE', 'house',
    [(750,270,210,100),(590,220,190,150),(420,170,190,160),(250,220,190,150),(0,270,300,100),(340,330,300,180)],
    [(270,250,55,32),(625,250,55,32),(410,365,52,30),(535,365,52,30)], (920,320), 'right', (944,320), 'childroom', 'NONNA ORA', (480,400), 'memory',
    [('VOCE','La casa non e quella in cui vivi adesso. E quella che la memoria ha ricostruito con le stanze che non hai avuto il coraggio di visitare.'),('VOCE','Una sedia vicino alla finestra e rivolta verso la porta. Qualcuno aspettava che tu tornassi a sederti.')],
    [('NONNA ORA','Non devi trovare tre ricordi. Devi fermarti accanto alla sedia e lasciare che il corpo ricordi prima della testa.'),('NONNA ORA','Poi potrai entrare nella stanza in cui avete litigato. Non tutto quello che fa male deve restare chiuso.')],
    props=[{'name':'La sedia vicino alla finestra','pos':(480,430),'lines':[('SEDIA','La sedia scricchiola. Per un attimo senti due voci che ridono, poi una frase: “Non serve che tu faccia finta di stare bene con me.”'),('VOCE','Non ricordi la risposta. Ricordi che quella volta non mentisti.')] }]),
'childroom': area(8, 'LA STANZA DEI GIORNI LUNGHI', 'bedroom',
    [(0,275,300,100),(240,220,200,150),(400,160,180,175),(420,0,140,180),(540,220,200,150),(660,275,300,100),(400,310,180,220),(420,500,140,140)],
    [(250,240,70,34),(610,240,70,34),(450,365,80,40),(460,470,60,20)], (40,320), 'up', (480,10), 'attic', 'IL RICORDO', (500,300), 'choice',
    [('VOCE','Sul muro ci sono due altezze segnate a matita. Una tua, una di Neri. La seconda si ferma tre anni fa.'),('VOCE','La stanza e piu piccola di come la ricordavi. Il silenzio, invece, e cresciuto.')],
    [('RICORDO','Nel vostro ultimo litigio, hai detto “fai come vuoi”. Non era quello che pensavi. Ma lei non poteva sentire la frase che avevi tenuto in testa.'),('RICORDO','Vuoi ricordare cosa avresti voluto dire, o preferisci restare con le parole che hai davvero pronunciato?')],
    options=[('DIRE LA VERITA','“Avevo paura che partire significasse perderti.”'),('DIFENDERTI','“Non spettava a me chiederti di restare.”'),('NON SAPERLO','“Non so ancora cosa avrei dovuto dire.”')]),
'attic': area(8, 'LA SOFFITTA DELLA VERGOGNA', 'attic',
    [(400,470,160,170),(330,345,300,150),(210,260,540,110),(300,130,360,160),(400,0,160,160),(0,280,230,90),(730,280,230,90)],
    [(280,300,52,42),(628,300,52,42),(390,380,38,30),(525,380,38,30)], (480,590), 'up', (480,10), 'archive', 'IL CUSTODE DEI RIFLESSI', (480,260), 'stealth',
    [('VOCE','La soffitta e piena di specchi coperti da lenzuola. Sotto ognuno c’e una versione di te che si vergogna di qualcosa di diverso.'),('VOCE','Un riflettore si accende. Quando ti illumina, senti il bisogno di diventare invisibile.')],
    [('IL CUSTODE DEI RIFLESSI','I riflettori cercano ogni cosa che provi a nascondere.'),('IL CUSTODE DEI RIFLESSI','Usa le zone d’ombra e raggiungi i quattro segni sul pavimento. Non devi sparire: devi attraversare la luce quando passa.')], route=[(250,320),(400,270),(570,320),(700,390)]),
'archive': area(9, 'L’ARCHIVIO DEL PRIMO GIORNO', 'archive',
    [(400,470,160,170),(320,350,320,170),(205,250,550,125),(300,130,360,160),(0,280,250,90),(710,280,250,90)],
    [(310,155,32,70),(355,155,32,70),(400,155,32,70),(570,155,32,70),(615,155,32,70),(660,155,32,70),(350,390,36,40),(575,390,36,40)], (480,590), 'right', (944,320), 'printroom', 'L’ARCHIVISTA', (480,300), 'sequence',
    [('VOCE','Qui ogni ricordo ha una data, ma tu hai continuato a leggerli al contrario: prima il rimorso, poi la paura, infine quello che e successo davvero.'),('VOCE','La cronologia non aggiusta il passato. Impedisce soltanto al tuo rimorso di riscriverlo da solo.')],
    [('ARCHIVISTA','Metti in ordine gli eventi come sono accaduti: la notizia della partenza, l’ultimo litigio, il treno che se ne va.'),('ARCHIVISTA','Nessuno ti chiede di scegliere quale momento fa piu male. Soltanto di smettere di confonderli.')],
    props=[{'name':'La partenza annunciata','pos':(330,285),'lines':[('REGISTRO','Neri ti disse che sarebbe partita. Tu facesti finta che non ti importasse.')]},{'name':'L’ultimo litigio','pos':(480,420),'lines':[('REGISTRO','Dicesti “fai come vuoi”. Volevi dire “ho paura”.')]},{'name':'Il treno','pos':(645,285),'lines':[('REGISTRO','La mano si alzo quando il vagone era gia lontano. Il treno non si fermo, ma il saluto esiste comunque.')] }], order=[0,1,2]),
'printroom': area(9, 'LA TIPOGRAFIA DEI DUBBI', 'press',
    [(0,280,300,100),(220,235,230,140),(400,180,200,160),(570,235,170,140),(700,280,260,100),(400,330,180,310)],
    [(255,260,50,38),(325,260,50,38),(610,260,45,38),(670,260,45,38),(440,390,45,30),(515,390,45,30)], (40,320), 'down', (480,630), 'platform_final', 'IL TIPOGRAFO', (490,380), 'sequence',
    [('VOCE','La macchina stampa domande a una velocita impossibile. Ogni foglio sembra una prova, ma nessuno porta una firma.'),('VOCE','Una domanda ti si appiccica alla giacca: “E se avessi capito male tutto?”')],
    [('IL TIPOGRAFO','La macchina ha stampato tre frammenti fuori ordine. Trova prima la notizia della partenza, poi il litigio, infine il treno.'),('IL TIPOGRAFO','Non cercare la risposta perfetta. Rimetti gli eventi nell’ordine in cui sono accaduti.')], props=[{'name':'LA NOTIZIA','pos':(280,290),'lines':[('REGISTRO','Neri ti disse che avrebbe accettato il corso.') ]},{'name':'IL LITIGIO','pos':(480,350),'lines':[('REGISTRO','Hai detto “fai come vuoi” quando avresti voluto dire “ho paura”.')]},{'name':'IL TRENO','pos':(670,290),'lines':[('REGISTRO','Il treno è partito. Il saluto è arrivato tardi, ma è comunque esistito.')] }], order=[0,1,2]),
'platform_final': area(10, 'LA BANCHINA SPEZZATA', 'void',
    [(400,0,160,140),(320,105,320,100),(200,185,260,100),(500,185,260,100),(0,280,285,90),(260,265,440,110),(120,365,240,100),(600,365,240,100),(400,360,160,115),(390,455,180,185)],
    [(430,35,30,28),(500,35,30,28),(290,210,28,25),(650,210,28,25),(160,390,30,27),(760,390,30,27)], (480,45), 'left', (10,320), 'witness', 'LA VOCE SULLA BANCHINA', (480,300), 'route',
    [('VOCE','La banchina si interrompe nel vuoto. Per raggiungere la figura devi camminare sui ricordi che hai smesso di chiamare errori.'),('VOCE','Non ci sono oggetti da raccogliere. Ci sono tre tratti di strada che devi attraversare senza voltarti a cercare un’altra versione del passato.')],
    [('VOCE','Prima la piattaforma spezzata. Poi il ponte sottile. Infine la luce. Non devi correre. Devi scegliere di fare il passo successivo.')],
    route=[(300,230),(660,230),(480,520)]),
'witness': area(10, 'LA STANZA CHE TI ASPETTA', 'final',
    [(750,280,210,100),(610,225,190,145),(430,185,220,140),(250,225,190,145),(0,280,300,100),(340,330,300,180)],
    [(280,250,55,35),(625,250,55,35),(410,365,45,30),(520,365,45,30)], (920,320), None, None, None, 'ACCETTAZIONE', (480,300), 'final_battle',
    [('VOCE','La figura ha il tuo stesso passo. Per tutto il viaggio hai creduto che fosse l ultimo ostacolo prima di Neri. Ma non ha mai avuto il suo volto.'),('VOCE','La stanza sembra aspettare una risposta. Il Testimone non ti attacca subito: ti guarda come se ricordasse ogni porta che hai aperto per non guardare la banchina.')],
    [('ACCETTAZIONE','Non sono Neri. Sono rimasto alla stazione insieme a te, nel punto in cui continui a chiederti se una frase diversa avrebbe cambiato tutto.'),('ACCETTAZIONE','Non ti dirò cosa sono. Non ancora. Prima devi decidere se vuoi continuare a lottare contro il ricordo o lasciare che ti raggiunga.'),('ACCETTAZIONE','Se la porta si aprisse e Neri non fosse dall altra parte, sapresti ancora chi sei?')], battle='witness', options=[('PORTARLO CON TE','Ti ricordi senza restare prigioniero del momento.'),('LASCIARLO ANDARE','Smetti di chiedere al ricordo di custodire il tuo presente.'),('RESTARE CON LUI','Non lo cancelli e non gli obbedisci: impari ad ascoltarlo.')]),
}

STORY_AREAS['room']['events'] = [
    [('RICORDO', 'Il bicchiere e pieno. Hai continuato a preparare due tazze anche quando nessuno veniva a bere la seconda.')],
    [('RICORDO', 'La sedia e vuota, ma il legno conserva il segno di una giacca appoggiata al bordo. Non devi cancellarlo per poter uscire.')],
    [('VOCE', 'Il posto vuoto non e una porta da aprire. E un posto vuoto. Non sei obbligato a riempirlo prima di andare avanti.')],
]


# Additional story spaces: these are narrative set-pieces, not rooms that ask for three pickups.
STORY_AREAS.update({
'tram': area(2, 'IL TRENO CHE NON PARTE', 'train',
    [(0,280,285,100),(205,240,250,150),(375,175,190,170),(505,225,245,145),(710,270,250,100),(410,0,145,210)],
    [(275,258,42,23),(535,250,42,23),(682,295,32,22)], (45,320), 'up', (480,10), 'tower', 'IL CAPOCORSA', (240,320), 'chase',
    [('VOCE','Il treno si ferma con tutte le luci accese, ma nessun macchinista al posto di guida.'),('VOCE','Sul tabellone lampeggia: REGISTRAZIONE SIGILLATA — ACCESSO NEGATO. Qualcuno ha messo una chiave tra te e l ultimo messaggio di Neri.'),('VOCE','Il Capocorsa scende e si allontana verso la carrozza vuota. Non ti sta trascinando in un ricordo: ti sta mostrando una traccia concreta.')],
    [('CAPOCORSA','La registrazione non e nella carrozza principale. Qualcuno l ha chiusa dietro una serratura della torre di segnalazione.'),('CAPOCORSA','Segui le mie tappe fino alla fine. Poi torna alla porta con il simbolo: il registro dei bagagli ti dira dove trovare la chiave.')],
    route=[(240,320),(425,275),(600,290),(790,320)]),
'underpass': area(3, 'IL SOTTOPASSAGGIO DELLE VOCI', 'underpass',
    [(0,280,240,95),(180,245,230,145),(350,300,240,95),(540,245,230,145),(730,280,230,95),(395,350,170,190),(400,520,160,120)],
    [(95,260,34,30),(270,300,36,24),(390,335,34,22),(620,280,34,22),(785,300,36,25)], (45,320), 'down', (480,630), 'alley', 'LA RAGAZZA DEL SOTTOPASSAGGIO', (120,320), 'stealth',
    [('VOCE','Le pareti ripetono tre versioni della stessa discussione. Nessuna voce era presente dall inizio alla fine.'),('VOCE','Un fascio di luce attraversa il tunnel come una domanda insistente. Quando ti trova, le parole tornano a sovrapporsi.'),('VOCE','Le ombre ai lati non sono oggetti da raccogliere: sono pause. Aspetta che la luce passi e attraversa lo spazio senza farti definire dalle voci.')],
    [('RAGAZZA','Io sentii solo “fai come vuoi”. Un uomo sul ponte senti solo il silenzio dopo. La venditrice ricorda una risata prima della lite.'),('RAGAZZA','Non ti sto chiedendo di dimostrare chi ha ragione. Devi attraversare il sottopassaggio senza prendere una frase isolata per tutta la storia.')],
    route=[(205,285),(700,285),(480,560)]),
'indexroom': area(4, 'L INDICE DELLE PAROLE', 'index',
    [(0,285,190,100),(145,245,230,160),(320,200,320,120),(430,280,150,200),(370,445,220,195),(620,245,200,140),(790,285,170,100)],
    [(215,280,30,55),(255,280,30,55),(295,280,30,55),(650,280,30,55),(690,280,30,55),(730,280,30,55)], (35,330), 'down', (480,630), 'pages', 'LUMA', (480,320), 'conversation',
    [('VOCE','Dietro la biblioteca c e un indice di lettere mai spedite. Qui le frasi non sono ordinate per autore, ma per quello che chi le scriveva sperava di ottenere.'),('VOCE','La busta di Neri non contiene una richiesta di salvataggio. Contiene l inizio di una frase che non riuscisti ad ascoltare fino in fondo.')],
    [('LUMA','La prima parte e chiara: “Non devi venire per dimostrarmi che ti importa”. Il resto non lo completerò io al posto tuo.'),('LUMA','Come la leggi? Come un rifiuto, come un confine o come una persona che prova a non renderti responsabile della propria scelta?')],
    options=[('UN RIFIUTO','Pensi che Neri non volesse piu averti accanto.'),('UN CONFINE','Pensi che ti stesse lasciando scegliere liberamente.'),('NON SO','Ammetti che una frase non basta a conoscere tutta una persona.')]),
'corridor': area(5, 'IL CORRIDOIO CHE RESPIRA', 'corridor',
    [(400,0,160,160),(320,130,320,100),(200,210,560,100),(90,280,780,100),(380,360,200,165),(400,510,160,130)],
    [(235,235,54,26),(675,235,54,26),(300,300,38,22),(620,300,38,22)], (480,45), 'down', (480,630), 'room', 'IL PENDOLO', (480,180), 'memory_walk',
    [('VOCE','L orologio della sala d attesa riparte, ma nessuno si alza. Una sedia vuota e stata lasciata al centro del corridoio.'),('VOCE','La sedia non contiene Neri. Contiene il posto che le avevi tenuto senza chiederti se volesse davvero restare.'),('VOCE','Attraversa i segni sul pavimento. Non devi seguire nessuno: guarda i dettagli che sono rimasti dopo la partenza.')],
    [('IL PENDOLO','Neri era venuta qui prima di partire. Non per essere convinta a restare. Voleva salutarti, ma non poteva vivere al posto tuo la paura di quel saluto.'),('IL PENDOLO','I dettagli sono ancora qui. Non sono una pista per ritrovarla: sono pezzi di una giornata che puoi finalmente ricordare.')],
    route=[(480,180),(285,300),(665,300),(480,430),(480,560)]),
'dressing': area(6, 'IL CAMERINO DELLE VOCI', 'dressing',
    [(0,280,320,100),(250,230,260,140),(410,130,140,125),(640,230,320,140),(380,330,200,180),(410,500,140,140)],
    [(300,260,34,30),(630,260,34,30),(435,385,28,25),(500,385,28,25)], (480,590), 'up', (480,10), 'stage', 'LA CAPOCOMICA', (480,300), 'memory_walk',
    [('VOCE','Dietro il palco, le maschere sono appese a chiodi diversi. Una ha la tua espressione quando fai finta che vada tutto bene; un altra, il sorriso che usi quando vuoi cambiare discorso.'),('VOCE','Non devi indossarle e non devi raccoglierle. Attraversa i segni sul pavimento: ognuno riporta a una battuta che hai recitato senza accorgertene.')],
    [('CAPOCOMICA','Io insegno a recitare, non a fingere per sempre. Cammina sul palco vuoto. I segni ti faranno sentire la battuta, ma non ti diranno quale personaggio devi essere.')],
    route=[(250,320),(480,190),(700,320),(480,440)]),
'island': area(7, 'LE ISOLE DELLA MAREA', 'island',
    [(0,280,210,100),(180,240,220,140),(365,280,230,95),(560,320,180,145),(710,280,250,100),(420,410,160,130)],
    [(90,300,36,26),(260,270,32,22),(445,300,34,22),(615,360,30,22),(795,300,36,24)], (45,320), 'right', (944,320), 'mirrorlake', 'IL BARCAIOLO', (180,300), 'tidal',
    [('VOCE','La riva si divide in isole. La marea scopre un passaggio e poi lo cancella, ma non sempre nello stesso punto.'),('VOCE','Il barcaiolo non ti chiede di raccogliere pietre o seguire una linea luminosa. Ti chiede di imparare il ritmo dell acqua: avanza quando si ritira, aspetta quando torna.')],
    [('BARCAIOLO','Neri scrisse: “Non devi salvarmi da una scelta che ho fatto io”. Non era una porta chiusa in faccia a te. Era una responsabilita rimessa nelle mani giuste.'),('BARCAIOLO','Attraversa le isole con la bassa marea. Se l acqua sale, fermati: non e una punizione, e un tempo diverso.')],
    route=[(195,300),(410,300),(610,370),(815,320)]),
'dining': area(8, 'LA TAVOLA APPARECCHIATA PER DUE', 'dining',
    [(0,280,960,100),(150,230,660,170),(350,150,260,140),(350,360,260,170),(0,280,130,100),(830,280,130,100)],
    [(345,260,50,25),(420,260,50,25),(495,260,50,25),(570,260,50,25),(375,385,42,25),(540,385,42,25)], (910,320), 'left', (10,320), 'childroom', 'NERI, COME LA RICORDI', (480,330), 'conversation',
    [('VOCE','Il tavolo e apparecchiato per due. La memoria ti presenta una Neri che non coincide del tutto con la persona reale: questa e la versione che hai ripetuto a te stesso per anni.'),('NERI','Non voglio fare l ultima discussione un altra volta. Voglio capire perche hai trasformato il fatto che io partissi nella prova che non ti volevo bene.')],
    [('NERI','Quando ti dissi che sarei partita, avevo gia accettato il corso e firmato il contratto. La lite non creo la mia scelta. Ma il tuo “fai come vuoi” mi fece pensare che non volessi salutarmi.'),('NERI','Non devi assolvermi e non devi assolvere te stesso in una frase. Possiamo provare a raccontare quel giorno in due parti?')],
    options=[('ERO ARRABBIATO','Ammetti che eri arrabbiato, anche se non era tutta la verita.'),('AVEVO PAURA','Ammetti che la partenza ti faceva paura.'),('NON RICORDO','Ammetti che la memoria ha coperto parte della scena.')]),
'timeline': area(9, 'IL NASTRO RIAVVOLTO', 'timeline',
    [(400,0,160,150),(300,110,360,140),(180,220,600,120),(0,280,270,100),(690,280,270,100),(330,320,300,170),(400,470,160,170)],
    [(320,145,30,45),(360,145,30,45),(600,145,30,45),(640,145,30,45),(385,360,32,30),(545,360,32,30)], (480,590), 'up', (480,10), 'printroom', 'L ARCHIVISTA', (480,300), 'memory_walk',
    [('VOCE','Il nastro si avvolge da solo. Quando provi a riavvolgere un ricordo, le immagini corrono all indietro piu veloci delle spiegazioni.'),('VOCE','Invece di prendere tre documenti, cammina dentro la sequenza. I momenti si attiveranno sotto i tuoi piedi, e questa volta non potrai saltare direttamente al finale.')],
    [('ARCHIVISTA','Prima la notizia del corso. Poi il litigio. Infine la banchina. Il tuo rimorso li ha sempre mostrati al contrario perche partire dal finale rende tutto piu semplice: qualcuno deve essere colpevole.'),('ARCHIVISTA','Cammina nel giusto ordine e resta finche ogni scena non finisce di parlare.')],
    route=[(480,520),(250,280),(705,280),(480,155)]),
'threshold': area(10, 'IL PASSAGGIO DEL DOVERE', 'threshold',
    [(400,0,160,150),(320,115,320,105),(210,200,260,100),(500,200,260,100),(0,280,300,100),(250,265,460,115),(660,280,300,100),(380,365,200,125),(400,480,160,160)],
    [(350,145,30,25),(580,145,30,25),(250,225,32,25),(680,225,32,25),(430,395,30,22),(500,395,30,22)], (480,45), 'down', (480,630), 'witness', 'IL DOVERE', (480,300), 'memory_walk',
    [('VOCE','Prima della stanza oltre la porta, tre frammenti del viaggio riaffiorano sul pavimento.'),('IL DOVERE','La banchina, il litigio, la notizia della partenza. Attraversali nell’ordine in cui sono accaduti.'),('VOCE','Oltre questa soglia c’è la figura che hai seguito per tutto il viaggio. Non puoi più rimandare l’incontro.')],
    [('IL DOVERE','Tre scene ti separano dalla stanza oltre la porta. Non sono prove da superare: sono ricordi che hai trasformato in una punizione.'),('IL DOVERE','Attraversali nell’ordine in cui sono accaduti. Poi entra senza chiedere al passato di cambiare.')], route=[(280,245),(680,245),(480,410)], events=[[('RICORDO','La notizia: Neri aveva già scelto il corso prima del litigio.')],[('RICORDO','Il litigio: avresti voluto chiedere di restare, ma non l’hai detto.')],[('RICORDO','La banchina: il treno è partito. Non c’era una frase segreta che lo avrebbe fermato.')]])
})

# Wire the rooms as a chapter-long route, with entries/doors changing direction frequently.
_NEXT_LINKS = {
'platform':'garden','garden':'node','node':'bells','bells':'tram','tram':'tower','tower':'market',
'market':'underpass','underpass':'alley','alley':'library','library':'indexroom','indexroom':'pages',
'pages':'waiting','waiting':'corridor','corridor':'room','room':'lobby','lobby':'dressing','dressing':'stage',
'stage':'shore','shore':'island','island':'mirrorlake','mirrorlake':'hall','hall':'dining','dining':'childroom',
'childroom':'attic','attic':'archive','archive':'timeline','timeline':'printroom','printroom':'platform_final',
'platform_final':'threshold','threshold':'witness','witness':None}
for _sid, _next in _NEXT_LINKS.items():
    STORY_AREAS[_sid]['next'] = _next

# The archive now unfolds through walking flashbacks rather than another three-item checklist.
STORY_AREAS['archive']['task'] = 'memory_walk'
STORY_AREAS['archive']['props'] = []
STORY_AREAS['archive']['order'] = []
STORY_AREAS['archive']['route'] = [(480,520),(260,300),(700,300),(480,155)]
STORY_AREAS['archive']['npc_lines'] = [('ARCHIVISTA','Prima il giorno in cui Neri ti disse del corso. Poi il litigio. Infine la stazione. Il rimorso li ha sempre mostrati al contrario.'),('ARCHIVISTA','Attraversa i punti del ricordo nell ordine in cui sono successi. Questa volta non puoi saltare direttamente al finale.')]
STORY_AREAS['archive']['events'] = [
 [('VOCE','DUE SETTIMANE PRIMA. Neri aveva gia ricevuto la conferma del corso. Ti racconto la notizia mentre tornavate a casa, e tu le rispondesti che era una cosa bella.'),('VOCE','Questo ricordo esiste anche se, anni dopo, la rabbia ti ha fatto dimenticare la tua felicita per lei.')],
 [('NERI','Quando ti dissi che sarei partita, non ti chiesi di fermarmi. Ti chiesi se saresti venuto alla stazione. Tu rispondesti: “Vedremo”.'),('VOCE','La paura si travesti da indifferenza, ma non divento per questo la verita intera.')],
 [('VOCE','IL LITIGIO. Hai detto “fai come vuoi”. Neri ti rispose che non voleva essere una decisione da approvare o respingere.'),('NERI','Avrei voluto che mi dicessi che ti sarei mancata. Non per farmi cambiare idea. Per sapere che la nostra amicizia avrebbe continuato a esistere dopo la partenza.')],
 [('VOCE','LA BANCHINA. Sei arrivato quando il treno era gia in movimento. Neri guardo fuori, ma non puoi sapere se ti vide. Il ricordo non fornisce una risposta solo perche la desideri.'),('VOCE','Questo e tutto quello che sai. Non e poco, ma non e abbastanza per condannarti per il resto della vita.')]
]
STORY_AREAS['timeline']['events'] = [
 [('VOCE','IL CORSO. La prima notizia non era una minaccia al vostro legame. Era una porta che Neri aveva trovato per se stessa.')],
 [('NERI','IL LITIGIO. Quando hai detto “fai come vuoi”, ho pensato che fossi arrabbiato. Non potevo sapere che avevi paura; tu non me lo avevi detto.')],
 [('VOCE','LA PARTENZA. Tu non l hai liberata dal treno e non l hai trattenuta. La tua esitazione fece male, ma non decise da sola la sua vita.')],
 [('VOCE','L AUDIO NON ASCOLTATO. La registrazione finisce cosi: “Non devi venire per riparare tutto. Se vieni, vieni per salutarmi. Se non ci riesci, io andro lo stesso. Ti voglio bene comunque”.'),('VOCE','Non e una assoluzione inventata dal ricordo. E una cosa che lei ti disse, e che tu non eri riuscito ad ascoltare fino alla fine.')]
]
STORY_AREAS['timeline']['route'] = [(480,520),(260,300),(700,300),(480,155)]
# Small map connectivity corrections verified against the same collision rectangles as movement.
STORY_AREAS['platform_final']['route'] = [(240,250),(700,250),(480,520)]
STORY_AREAS['dressing']['floors'].append((530,280,140,100))
STORY_AREAS['dressing']['floors'].append((410,0,140,150))
STORY_AREAS['island']['blocks'] = [b for b in STORY_AREAS['island']['blocks'] if b[0] != 795]
STORY_AREAS['island']['route'] = [(195,300),(410,300),(610,370),(870,340)]

# Multi-turn conversations create a real exchange instead of one isolated menu choice.
STORY_AREAS['indexroom']['second_options'] = [('ASCOLTARE','Vuoi sentire il resto della registrazione.'),('FARE UNA DOMANDA','Vuoi chiedere cosa non sai, senza riempire il vuoto.'),('FERMARTI','Vuoi lasciare incompleta una parte che non puoi conoscere.')]
STORY_AREAS['indexroom']['second_prompt'] = 'COME VUOI CONTINUARE?'
STORY_AREAS['indexroom']['responses'] = [
 [('LUMA','Capisco. Un rifiuto e piu facile da sopportare di una scelta che non riguarda soltanto te.'),('VOCE','Ma una frase puo avere un confine senza essere un addio all affetto.')],
 [('LUMA','Un confine non e un giudizio su quanto vali. Ti dice soltanto dove finisce la responsabilita di una persona e comincia quella dell altra.'),('VOCE','La busta pesa meno, ma non contiene tutte le risposte.')],
 [('LUMA','Non sapere non significa che devi inventare una versione per riempire il silenzio.'),('VOCE','Puoi continuare senza avere la frase completa.')]
]
STORY_AREAS['indexroom']['second_results'] = [
 [('LUMA','La registrazione e gia qui. Non posso decidere quando sarai pronto ad ascoltarla.'),('VOCE','La biblioteca apre la sala successiva: non perche la risposta sia perfetta, ma perche hai scelto cosa farne.')],
 [('LUMA','La domanda giusta non e “perche mi hai lasciato?”. E “che cosa non so della tua scelta?”.'),('VOCE','Non potrai chiedere a Neri ogni risposta. Puoi smettere di inventare quelle che ti puniscono.')],
 [('LUMA','Lasciare una frase incompleta non significa cancellarla. Significa rispettare la parte che non ti appartiene.'),('VOCE','La pagina rimane aperta. La storia puo proseguire senza essere finita.')]
]
STORY_AREAS['dining']['second_options'] = [('CHIEDERE SCUSA','Ti scusi per come hai parlato, senza pretendere una risposta.'),('DIRE CHE TI MANCA','Nomini la perdita senza chiedere a Neri di rimediare.'),('CHIEDERE DI RESTARE','Provi ancora a cambiare il finale del ricordo.')]
STORY_AREAS['dining']['second_prompt'] = 'CHE COSA LE DICI ADESSO?'
STORY_AREAS['dining']['responses'] = [
 [('NERI','La rabbia era vera. Anche la paura era vera. Non serve sceglierne una sola e fingere che l altra non esistesse.')],
 [('NERI','Lo so. Mi sei mancato anche tu. Ma mancarsi non significa che una persona debba restare ferma per l altra.')],
 [('NERI','Una parte di me avrebbe voluto sentirlo. Ma non potevo prometterti che sarei rimasta, e non volevo che la tua vita diventasse una sala d attesa.')]
]
STORY_AREAS['dining']['second_results'] = [
 [('NERI','Grazie. Non mi chiedi di cancellare il litigio: riconosci che e successo.'),('VOCE','La tavola non scompare, ma le due sedie non sono piu inchiodate al pavimento.')],
 [('NERI','Mi fa bene sapere che ti sono mancata. Non e una promessa di ritorno. E un pezzo vero della nostra amicizia.'),('VOCE','Per la prima volta, il ricordo puo contenere affetto e distanza nello stesso momento.')],
 [('NERI','Avrei voluto restare in quella sera, forse. Ma la vita non si puo ridurre a un solo desiderio.'),('VOCE','La tua scelta non cambia il passato. Cambia il modo in cui entri nella prossima stanza.')]
]


STORY_AREAS['corridor']['events'] = [
    [('RICORDO', 'Il bicchiere e pieno. Hai continuato a preparare due tazze anche quando nessuno veniva a bere la seconda.')],
    [('RICORDO', 'La sedia e vuota, ma il legno conserva il segno di una giacca appoggiata al bordo. Non devi cancellarlo per poter uscire.')],
    [('VOCE', 'Il posto vuoto non e una porta da aprire. E un posto vuoto. Non sei obbligato a riempirlo prima di andare avanti.')],
    [('VOCE', 'Il corridoio termina. Non hai trovato Neri, ma hai smesso per un momento di cercare una persona dentro agli oggetti.')],
    [('VOCE', 'Ora puoi passare alla stanza successiva senza che qualcuno ti accompagni e senza dover meritare di essere li.')],
]

# Optional two-room key hunt in the train: clue first, physical key second.
STORY_AREAS['tram']['props'].append({
    'name': 'Porta della carrozza laterale', 'pos': (850, 340),
    'side_room': 'baggage_car',
    'lines': [('PORTA', 'La serratura ha un simbolo della cabina di segnalazione. Prima devi capire quale chiave cerca.')]
})
STORY_AREAS['baggage_car'] = area(2, 'CARROZZA BAGAGLI', 'baggage',
    [(0,280,960,100),(95,215,220,150),(360,185,240,175),(645,215,220,150)],
    [(150,248,52,24),(410,228,52,24),(700,248,52,24)], (45,320), 'right', (944,326), 'signal_cabin',
    'REGISTRAZIONE', (820,300), 'search_room',
    [('VOCE','La carrozza puzza di carta bagnata e ferro caldo. Le etichette sui bagagli hanno tutte una destinazione, tranne una.'),
     ('VOCE','La serratura non vuole una chiave qualsiasi. Sul telaio e inciso: “prima il numero, poi il segnale”.')],
    [('VOCE','Cerca il registro di carico. Se trovi il numero della cabina, saprai dove cercare la chiave.')],
    props=[
        {'name':'Registro di carico', 'pos':(455,320), 'key_item':'numero_cabina',
         'key_found_text':'Hai trovato il codice della cabina di segnalazione.',
         'lines':[('REGISTRO','Carrozza 03: la chiave di servizio e stata spostata alla cabina S-17.'),('VOCE','Il numero e un indizio, non una chiave. La carrozza successiva porta il simbolo S-17.') ]},
        {'name':'Valigia senza etichetta', 'pos':(245,320),
         'lines':[('VALIGIA','Dentro c e un maglione piegato con cura. Sul biglietto: “Non trasformare ogni assenza in un enigma da risolvere”.')]},
        {'name':'Carrello ribaltato', 'pos':(710,320),
         'lines':[('CARRELLO','Il metallo vibra al passaggio del treno. Qualcuno ha cercato in fretta, ma ha lasciato il registro al suo posto.')]}
    ])
STORY_AREAS['signal_cabin'] = area(2, 'CABINA S-17', 'signal',
    [(0,280,960,100),(125,220,200,150),(365,165,230,205),(635,220,200,150)],
    [(170,250,46,25),(700,250,46,25),(445,205,26,20),(490,205,26,20)], (30,326), 'right', (944,326), None,
    'TERMINALE', (820,300), 'search_room',
    [('VOCE','La cabina di segnalazione e accesa, anche se il treno non dovrebbe avere corrente.'),
     ('TERMINALE','S-17 riconosciuta. La chiave e stata lasciata nel cassetto di emergenza. Non aprire il registro dei passeggeri: contiene una registrazione privata.')],
    [('TERMINALE','La serratura richiede una chiave metallica, non il codice. Il cassetto ha un fermo manuale sul lato destro.')],
    props=[
        {'name':'Cassetto di emergenza', 'pos':(480,330), 'key_item':'chiave_carrozza',
         'key_found_text':'CHIAVE DELLA CARROZZA ottenuta. Ora puoi tornare al treno e raggiungere la torre.',
         'lines':[('CASSETTO','Un clic secco. Dentro c e una chiave d ottone con inciso il simbolo della torre.'),('VOCE','Non hai trovato una scorciatoia: hai seguito l indizio fino alla stanza giusta. La chiave apre la porta laterale del treno.') ]},
        {'name':'Registro passeggeri', 'pos':(680,330),
         'lines':[('REGISTRO','Una busta e gia stata rimossa. Non trovi lettere da leggere, solo una riga: “consegnata alla persona giusta, al momento giusto”.')]}
    ])
for _side_id in ('baggage_car', 'signal_cabin'):
    STORY_AREAS[_side_id]['is_side_room'] = True

# Campaign flow: every authored room is now part of the actual game, not an unused side definition.
# The same ten chapters unfold over 31 connected scenes, with different tasks and exits.
SCENE_ORDER = ['platform','garden','node',
               'bells','tram','tower',
               'market','underpass','alley',
               'library','indexroom','pages',
               'waiting','corridor','room',
               'lobby','dressing','stage',
               'shore','island','mirrorlake',
               'hall','dining','childroom','attic',
               'archive','timeline','printroom',
               'platform_final','threshold','witness']
for _scene_i, _scene_key in enumerate(SCENE_ORDER):
    STORY_AREAS[_scene_key]['next'] = SCENE_ORDER[_scene_i + 1] if _scene_i + 1 < len(SCENE_ORDER) else None

# Paired doorways: each scene exits on a walkable edge and the next starts on the opposite edge.
TRANSITION_LAYOUT = {
    'platform': ('right', (944, 326), 'garden', (24, 322)),
    'garden': ('up', (486, 10), 'node', (466, 616)),
    'node': ('left', (10, 306), 'bells', (936, 326)),
    'bells': ('left', (10, 326), 'tram', (936, 318)),
    'tram': ('left', (10, 330), 'tower', (936, 318)),
    'tower': ('up', (454, 10), 'market', (486, 616)),
    'market': ('right', (944, 310), 'underpass', (24, 330)),
    'underpass': ('right', (944, 330), 'alley', (24, 326)),
    'alley': ('down', (506, 630), 'library', (486, 24)),
    'library': ('right', (944, 330), 'indexroom', (24, 334)),
    'indexroom': ('right', (944, 334), 'pages', (24, 330)),
    'pages': ('down', (498, 630), 'waiting', (482, 24)),
    'waiting': ('up', (482, 10), 'corridor', (482, 616)),
    'corridor': ('up', (482, 10), 'room', (482, 616)),
    'room': ('up', (482, 10), 'lobby', (482, 616)),
    'lobby': ('up', (482, 10), 'dressing', (478, 616)),
    'dressing': ('up', (478, 10), 'stage', (482, 616)),
    'stage': ('right', (944, 326), 'shore', (24, 334)),
    'shore': ('left', (10, 334), 'island', (936, 330)),
    'island': ('right', (944, 330), 'mirrorlake', (24, 330)),
    'mirrorlake': ('left', (10, 330), 'hall', (936, 318)),
    'hall': ('left', (10, 318), 'dining', (936, 330)),
    'dining': ('left', (10, 330), 'childroom', (936, 326)),
    'childroom': ('down', (490, 630), 'attic', (482, 24)),
    'attic': ('left', (10, 326), 'archive', (936, 326)),
    'archive': ('down', (482, 630), 'timeline', (482, 24)),
    'timeline': ('right', (944, 330), 'printroom', (24, 330)),
    'printroom': ('down', (490, 630), 'platform_final', (482, 24)),
    'platform_final': ('down', (478, 630), 'threshold', (482, 24)),
    'threshold': ('left', (10, 330), 'witness', (936, 330)),
}
for _source, (_exit, _door, _target, _spawn) in TRANSITION_LAYOUT.items():
    STORY_AREAS[_source]['exit'] = _exit
    STORY_AREAS[_source]['door'] = _door
    STORY_AREAS[_target]['spawn'] = _spawn
del _source, _exit, _door, _target, _spawn

CHAPTER_TITLES = {
    1: 'IL BIGLIETTO SENZA NOME', 2: 'LA CITTA CHE NON SA DIRE ADDIO',
    3: 'IL PREZZO DEL RICORDO', 4: 'LE PAROLE CHE MANCANO',
    5: 'L’ATTESA', 6: 'LE PARTI CHE RECITI',
    7: 'QUELLO CHE NON PUOI CONTROLLARE', 8: 'LA CASA DEL RICORDO',
    9: 'LA VERSIONE DEI FATTI', 10: 'IL SALUTO',
}
SCENES_BY_CHAPTER = {}
for _scene_key in SCENE_ORDER:
    SCENES_BY_CHAPTER.setdefault(STORY_AREAS[_scene_key]['chapter'], []).append(_scene_key)
del _scene_i, _scene_key
PALETTE_FOR_CHAPTER = {1:1, 2:3, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10}
BATTLE_NAMES = {
 'echo':('IL NODO','(silenzio)',(104,224,236)), 'guilt':('LA COLPA','(sentenza)',(255,190,111)),
 'denial':('IL RIFLESSO','(negazione)',(125,192,255)), 'perfection':('LA PERFEZIONE','(controllo)',(204,150,255)),
 'grief':('IL LUTTO','(onda / nucleo)',(115,211,220)), 'anger':('LA RABBIA','(scatto)',(255,110,140)),
 'fear':('LA PAURA','(luce sicura)',(255,218,117)), 'shame':('LA VERGOGNA','(riflettore)',(224,193,255)),
 'doubt':('IL DUBBIO','(rispondi)',(130,220,205)), 'witness':('IL TESTIMONE','(tre ricordi)',(255,205,225)),
 'control':('IL DOVERE','(la linea di controllo)',(255,176,104)),
 'bargaining':('LA CONTRATTAZIONE','(e se...)',(255,198,117)),
 'depression':('LA DEPRESSIONE','(il vuoto)',(139,166,222)),
}

BOSS_STAGE_SCENES = {
    'node': {'stage': 1, 'name': 'IL PORTIERE', 'subtitle': 'TORNA INDIETRO', 'color': (112, 195, 255)},
    'tower': {'stage': 2, 'name': 'IL GUARDIANO', 'subtitle': 'NON FARE UN ALTRO PASSO', 'color': (255, 93, 115)},
    'alley': {'stage': 3, 'name': 'IL MERCANTE', 'subtitle': 'POSSO DARTI UN ALTRO FINALE', 'color': (255, 196, 112)},
    'pages': {'stage': 4, 'name': 'LA SENTINELLA', 'subtitle': 'LEI NON TI VUOLE QUI', 'color': (150, 169, 230)},
}

class StoryGame(Game):
    def __init__(self):
        super().__init__()
        self.started = False
        self.ending = False
        self.scene_id = 'platform'
        self.scene_surface = self.build_story_map(self.scene_id)
        self.npc_pos = list(STORY_AREAS[self.scene_id]['npc_pos'])
        self.story_t = 0.0
        self.story_choices = {}
        self.inventory = set()
        self.side_return = None
        self.story_states = {k:{'clear':False,'talked':False,'props':set(),'progress':0,'route':0,'started':False,'conversation_stage':1,'last_checkpoint':None} for k in STORY_AREAS}
        self.choice_pending = False
        self.rhythm_active = False
        self.rhythm_clock = 0.0
        self.rhythm_hits = 0
        self.battle = None
        self.battle_active = False
        self.battle_flash = 0.0
        self.story_ending = None
        self.player = [65.0,320.0]
        self.walk_time = 0.0
        self.facing = (1,0)
        self.step_sound_timer = 0.0
        self.flash_timer = 0.0
        self.hint_timer = 0.0
        self.hint_text = ''
        self.room_title_timer = 0
        self.chapter = 1
        self.room = 1
        self.audio.set_music('ch01.ogg')

    @property
    def scene(self):
        return STORY_AREAS[self.scene_id]

    @property
    def state(self):
        return self.story_states[self.scene_id]

    @property
    def palette(self):
        return PALETTES[PALETTE_FOR_CHAPTER[self.scene['chapter']]]

    def begin_campaign(self):
        self.started = True
        self.enter_scene('platform', first=True)

    def enter_scene(self, scene_id, first=False, show_intro=True):
        self.scene_id = scene_id
        data = self.scene
        self.chapter = data['chapter']
        self.room = PALETTE_FOR_CHAPTER[self.chapter]
        self.player = [float(v) for v in data['spawn']]
        self.npc_pos = list(data.get('route',[data['npc_pos']])[0] if data['task']=='chase' else data['npc_pos'])
        self.facing = (1,0)
        self.room_title_timer = 3.2
        self.flash_timer = 0.22
        self.hint_timer = 0
        self.battle = None
        self.battle_active = False
        self.choice_pending = False
        self.rhythm_active = False
        self.scene_surface = self.build_story_map(scene_id)
        self.particles = [Particle(self.room, True) for _ in range(65)]
        self.audio.set_music(f'ch{self.chapter:02d}.ogg')
        intro=list(data['intro'])
        # Decisions are remembered by later scenes: the story responds instead of resetting
        # to the same generic dialogue after every room.
        if scene_id == 'underpass':
            market = self.story_choices.get('market', 1)
            intro.append(('VOCE', [
                'Al mercato hai scelto di guardare i fatti. Qui ogni voce e solo un pezzo del racconto: non scambiarne una per tutta la storia.',
                'Al mercato ti sei preso anche la colpa degli altri. Le voci del tunnel proveranno a convincerti che una responsabilita totale sia piu semplice di una verita complessa.',
                'Al mercato hai provato a comprare una via di fuga. Il tunnel non ti rincorre: continua semplicemente a esistere, anche quando chiudi gli occhi.'
            ][market - 1]))
        elif scene_id == 'pages':
            lib = self.story_choices.get('library', 3)
            intro.append(('LA PERFEZIONE', [
                'Hai ammesso che avevi paura. Io rendero quella frase cento volte piu elegante, finche non riconoscerai piu la tua voce.',
                'Hai capito che non volevi obbligarla a restare. Ora proverò a trasformare la cura in una regola impossibile da rispettare.',
                'Hai detto che non sai ancora tutto. La mia specialita e farti credere che l’incertezza sia un errore da correggere.'
            ][lib - 1]))
        elif scene_id == 'mirrorlake':
            choice = self.story_choices.get('lobby', 3)
            intro.append(('RIFLESSO', [
                'A teatro hai chiesto aiuto. Il lago ti mostra che essere visto non ti rende meno degno di affetto.',
                'A teatro hai lasciato parlare la rabbia. Ora puoi ascoltarla senza darle il controllo del ricordo.',
                'A teatro hai tenuto la maschera. L’acqua non te la strappa: ti mostra il costo di indossarla sempre.'
            ][choice - 1]))
        elif scene_id == 'timeline':
            dining = self.story_choices.get('dining', 2)
            intro.append(('VOCE', [
                'Hai chiesto scusa. Ma una scusa non e una macchina del tempo: serve a nominare la tua parte, non a riscrivere quella di Neri.',
                'Hai detto che ti e mancata. L’affetto non e una richiesta di ritorno; e un fatto che puo essere vero anche a distanza.',
                'Hai ammesso di aver desiderato che restasse. Il desiderio era umano. Il confine e cio che avresti fatto con quel desiderio.'
            ][dining - 1]))
            childhood = self.story_choices.get('childroom', 3)
            intro.append(('VOCE', [
                'Nella stanza d’infanzia hai ammesso che volevi salutarla. Questa memoria non ti chiede di vergognarti del desiderio.',
                'Hai riconosciuto la frase fredda che hai usato per proteggerti. Ora devi accettare che anche le parole difensive lasciano conseguenze.',
                'Hai lasciato aperta una domanda. Non e una sconfitta: e uno spazio in cui la tua memoria puo smettere di inventare.'
            ][childhood - 1]))
        elif scene_id == 'threshold':
            lobby = self.story_choices.get('lobby', 1)
            intro.append(('IL DOVERE', [
                'Hai imparato a chiedere aiuto. Io trasformero anche questo in un obbligo: adesso devi essere sempre capace di farlo.',
                'Hai dato voce alla rabbia. Io ti diro che devi restare arrabbiato per dimostrare che tenevi a lei.',
                'Hai tenuto la maschera. Io usero la maschera come una legge: se non sei perfetto, non meriti di andare avanti.'
            ][lobby - 1]))
        elif scene_id == 'witness':
            market=self.story_choices.get('market',1); dining=self.story_choices.get('dining',2)
            intro.append(('IL TESTIMONE', ['Al mercato hai scelto la verita. Adesso non usarla come un arma contro di te.','Al mercato hai preso su di te anche il peso che non era tuo. E arrivato il momento di separare le responsabilita.','Al mercato hai provato a fuggire. Eppure sei arrivato fin qui: anche quello e un modo di ricominciare.'][market-1]))
            intro.append(('IL TESTIMONE', ['Hai chiesto scusa senza pretendere assoluzione.','Hai detto che ti mancava senza chiedere a Neri di tornare.','Hai chiesto di restare. Il desiderio era sincero, ma non poteva diventare un obbligo per lei.'][dining-1]))
            lib = self.story_choices.get('library', 3)
            intro.append(('IL TESTIMONE', ['Hai riconosciuto la paura sotto la frase fredda.','Hai smesso di confondere il rispetto dei confini con l’assenza di affetto.','Hai accettato che alcune domande restino senza risposta.'][lib-1]))
        if show_intro:
            self.start_dialogue(intro)

    def build_story_map(self, scene_id):
        data = STORY_AREAS[scene_id]
        p = PALETTES[PALETTE_FOR_CHAPTER[data['chapter']]]
        rng = random.Random(90210 + sum(ord(c) for c in scene_id))
        surf = pygame.Surface((WIDTH,HEIGHT)).convert()
        surf.fill(tuple(max(0,c//3) for c in p['wall']))
        # Unique specks on void areas make broken/floating floors feel different from interiors.
        for _ in range(180):
            x,y=rng.randrange(WIDTH),rng.randrange(HEIGHT)
            surf.set_at((x,y), tuple(max(0,c//2) for c in p['line']))
        floors=[pygame.Rect(*r) for r in data['floors']]
        for r in floors:
            wall=r.inflate(15,15)
            pygame.draw.rect(surf, tuple(max(0,c-10) for c in p['wall']), wall, border_radius=3)
            pygame.draw.rect(surf, p['line'], wall, 2, border_radius=3)
        for ri,r in enumerate(floors):
            pygame.draw.rect(surf,p['floor'],r)
            for y in range(r.top//TILE,(r.bottom+TILE-1)//TILE):
                for x in range(r.left//TILE,(r.right+TILE-1)//TILE):
                    cell=pygame.Rect(x*TILE,y*TILE,TILE,TILE).clip(r)
                    shade=p['floor2'] if rng.random()<0.23 else p['floor']
                    pygame.draw.rect(surf,shade,cell)
                    if data['style'] in ('library','archive','paper','press'):
                        pygame.draw.line(surf,p['line'],(cell.left+3,cell.bottom-3),(cell.right-3,cell.bottom-3),1)
                    elif data['style'] in ('lake','mirrorlake'):
                        if (x+y)%2==0: pygame.draw.line(surf,tuple(min(255,c+12) for c in p['line']),(cell.left+5,cell.top+8),(cell.right-5,cell.top+10),1)
                    elif data['style'] in ('house','bedroom','attic'):
                        pygame.draw.rect(surf,p['line'],cell,1)
                    elif data['style'] in ('station','bells','market','theatre','stage'):
                        if rng.random()<0.14: pygame.draw.circle(surf,p['line'],(cell.centerx,cell.centery),2)
            pygame.draw.rect(surf,p['line'],r,1)
        # Style-specific architecture and floor markings.
        style=data['style']
        if style in ('bells','tower'):
            for x,y in ((175,245),(270,245),(665,245),(750,245)):
                if any(f.collidepoint(x,y) for f in floors):
                    pygame.draw.line(surf,(78,88,126),(x,y-22),(x,y-8),3)
                    pygame.draw.circle(surf,(255,218,145),(x,y),8,2)
                    pygame.draw.arc(surf,p['glow'],(x-8,y-7,16,14),0,math.pi,2)
        elif style in ('market',):
            awns=[(285,135,68,50,(234,109,142)),(385,135,68,50,(100,206,197)),(485,135,68,50,(244,198,111)),(645,260,48,32,(166,132,235))]
            for x,y,w,h,c in awns:
                pygame.draw.rect(surf,(36,27,52),(x,y,w,h),border_radius=3); pygame.draw.rect(surf,c,(x,y,w,h),2,border_radius=3)
                for xx in range(x+5,x+w-3,12): pygame.draw.line(surf,c,(xx,y+3),(xx+4,y+11),2)
        elif style in ('library','paper','archive','press'):
            for x,y,w,h in ((238,235,32,62),(280,235,32,62),(322,235,32,62),(630,235,32,62),(672,235,32,62),(714,235,32,62)):
                if any(f.colliderect(pygame.Rect(x,y,w,h)) for f in floors):
                    pygame.draw.rect(surf,(31,19,46),(x,y,w,h),border_radius=2); pygame.draw.rect(surf,(159,107,151),(x,y,w,h),1)
                    for yy in range(y+9,y+h-4,10): pygame.draw.line(surf,(201,148,175),(x+4,yy),(x+w-4,yy),2)
        elif style in ('hospital','hospitalroom'):
            for x,y in ((140,240),(255,240),(655,240),(765,330)):
                if any(f.collidepoint(x,y) for f in floors):
                    pygame.draw.rect(surf,(52,63,87),(x,y,68,27),border_radius=3); pygame.draw.rect(surf,(155,188,199),(x+4,y+4,17,10),1); pygame.draw.line(surf,(97,143,162),(x+5,y+22),(x+62,y+22),2)
        elif style in ('theatre','stage'):
            pygame.draw.rect(surf,(55,20,47),(305,118,350,112),border_radius=4)
            pygame.draw.rect(surf,(174,73,116),(305,118,350,112),2,border_radius=4)
            for x in range(320,650,25): pygame.draw.line(surf,(120,42,80),(x,120),(x+4,225),3)
            if style=='stage': pygame.draw.ellipse(surf,(255,200,128),(428,150,105,48),2)
            else:
                for y in (385,420):
                    for x in (330,390,570,630): pygame.draw.rect(surf,(57,32,58),(x,y,28,20),border_radius=3)
        elif style in ('lake','mirrorlake'):
            for x,y,w,h in ((85,300,40,15),(265,260,33,13),(485,285,34,15),(640,365,32,15),(450,475,35,14)):
                pygame.draw.ellipse(surf,(9,43,61),(x,y,w,h)); pygame.draw.ellipse(surf,(53,123,138),(x,y,w,h),1)
        elif style in ('house','bedroom','attic'):
            for x,y in ((270,250),(625,250)):
                pygame.draw.rect(surf,(39,48,59),(x,y,54,33),border_radius=3); pygame.draw.rect(surf,(143,164,169),(x,y,54,33),1,border_radius=3)
            if style=='bedroom':
                pygame.draw.rect(surf,(62,48,72),(420,340,110,65),border_radius=4); pygame.draw.rect(surf,(202,131,178),(420,340,110,65),2,border_radius=4)
        elif style=='void':
            for poly in [[(410,8),(550,8),(565,45),(548,110),(410,110),(390,57)],[(215,190),(440,190),(454,216),(439,270),(215,270),(198,227)],[(510,190),(745,190),(765,226),(744,270),(510,270),(495,224)]]:
                pygame.draw.polygon(surf,(36,39,75),poly); pygame.draw.polygon(surf,(138,116,200),poly,2)
        elif style=='train':
            pygame.draw.line(surf,(117,133,165),(0,350),(WIDTH,350),4)
            pygame.draw.line(surf,(117,133,165),(0,365),(WIDTH,365),4)
            for x in range(10,WIDTH,28): pygame.draw.line(surf,(75,93,131),(x,347),(x+9,368),2)
            for x in (270,420,570,720):
                pygame.draw.rect(surf,(32,43,66),(x,215,70,36),border_radius=5)
                pygame.draw.rect(surf,(121,208,223),(x+7,221,18,15),1); pygame.draw.rect(surf,(121,208,223),(x+35,221,18,15),1)
        elif style=='baggage':
            for x,y in ((125,236),(395,206),(675,236)):
                pygame.draw.rect(surf,(36,34,51),(x,y,72,54),border_radius=4)
                pygame.draw.rect(surf,(192,143,100),(x,y,72,54),2,border_radius=4)
                pygame.draw.line(surf,(192,143,100),(x+36,y+2),(x+36,y+52),2)
                pygame.draw.circle(surf,(232,205,153),(x+58,y+12),3)
            for x in (230,480,730):
                pygame.draw.line(surf,(100,125,158),(x,180),(x,210),3)
                pygame.draw.circle(surf,(228,190,130),(x,177),5,1)
        elif style=='signal':
            pygame.draw.rect(surf,(16,29,48),(380,185,200,84),border_radius=5)
            pygame.draw.rect(surf,(104,219,206),(380,185,200,84),2,border_radius=5)
            for i,c in enumerate(((93,229,204),(255,208,104),(251,113,155))):
                pygame.draw.circle(surf,c,(408+i*42,211),7)
            pygame.draw.rect(surf,(46,55,76),(430,236,100,24),border_radius=3)
            pygame.draw.rect(surf,(104,219,206),(430,236,100,24),1,border_radius=3)
            for x in (180,715):
                pygame.draw.rect(surf,(40,43,62),(x,228,58,38),border_radius=3)
                pygame.draw.rect(surf,(226,169,105),(x,228,58,38),1,border_radius=3)
                pygame.draw.line(surf,(226,169,105),(x+9,239),(x+49,239),1)
                pygame.draw.line(surf,(226,169,105),(x+9,248),(x+38,248),1)
        elif style=='underpass':
            for x in (40,240,440,640,840):
                pygame.draw.arc(surf,(58,74,105),(x,235,110,115),math.pi,2*math.pi,3)
                pygame.draw.line(surf,(58,74,105),(x,292),(x,365),3)
            pygame.draw.line(surf,(35,57,82),(0,258),(WIDTH,258),4)
            pygame.draw.line(surf,(35,57,82),(0,390),(WIDTH,390),4)
        elif style=='index':
            for r in (145,115,85):
                pygame.draw.ellipse(surf,(72,54,94),(480-r,320-r//2,2*r,r),1)
            for x in (230,275,320,640,685,730):
                pygame.draw.rect(surf,(42,30,57),(x,265,25,70),border_radius=2)
                for yy in range(272,330,10): pygame.draw.line(surf,(185,133,174),(x+4,yy),(x+21,yy),2)
        elif style=='corridor':
            for x in (145,315,485,655,825):
                pygame.draw.line(surf,(100,155,176),(x,225),(x,255),2)
                pygame.draw.rect(surf,(199,234,231),(x-9,222,18,6),border_radius=2)
            pygame.draw.line(surf,(105,137,168),(100,275),(860,275),2)
            pygame.draw.line(surf,(105,137,168),(100,375),(860,375),2)
        elif style=='dressing':
            for x in (80,260,440,620,800):
                pygame.draw.line(surf,(130,58,91),(x,220),(x,365),5)
                pygame.draw.arc(surf,(222,126,167),(x-26,236,52,70),0,math.pi,2)
            for x,y in ((255,320),(480,190),(700,320),(480,440)):
                pygame.draw.circle(surf,(238,201,137),(x,y),14,1); pygame.draw.circle(surf,(238,201,137),(x,y),5,1)
        elif style=='island':
            for y in (235,355,445):
                pygame.draw.line(surf,(21,77,104),(0,y),(WIDTH,y+int(math.sin(y)*8)),2)
            for x,y in ((195,300),(410,300),(610,370),(815,320)):
                pygame.draw.ellipse(surf,(89,117,130),(x-32,y-20,64,40)); pygame.draw.ellipse(surf,(160,203,195),(x-32,y-20,64,40),2)
        elif style=='dining':
            pygame.draw.rect(surf,(53,39,48),(320,274,320,88),border_radius=8)
            pygame.draw.rect(surf,(177,126,128),(320,274,320,88),2,border_radius=8)
            for x in (350,410,470,530,590):
                pygame.draw.circle(surf,(199,152,162),(x,265),10,2); pygame.draw.circle(surf,(199,152,162),(x,371),10,2)
            pygame.draw.circle(surf,(252,218,151),(480,317),9,2)
        elif style=='timeline':
            for x,y in ((260,280),(480,520),(700,280),(480,155)):
                pygame.draw.ellipse(surf,(42,44,79),(x-48,y-24,96,48),2)
                pygame.draw.line(surf,(123,135,199),(x-28,y),(x+28,y),1)
                pygame.draw.line(surf,(123,135,199),(x,y-12),(x,y+12),1)
        elif style=='threshold':
            for poly in [[(420,8),(540,8),(550,70),(490,112),(415,76)],[(230,206),(430,206),(445,238),(420,280),(240,280)],[(530,206),(730,206),(720,280),(550,280)],[(380,375),(580,375),(565,440),(395,440)]]:
                pygame.draw.polygon(surf,(47,34,59),poly); pygame.draw.polygon(surf,(255,176,104),poly,2)
        # Obstacles are both visible and solid. Their appearance depends on the location.
        for x,y,w,h in data['blocks']:
            if style in ('library','paper','archive','press'):
                pygame.draw.rect(surf,(34,22,46),(x,y,w,h),border_radius=2); pygame.draw.rect(surf,(155,104,150),(x,y,w,h),1)
                for yy in range(y+7,y+h-2,10): pygame.draw.line(surf,(190,139,162),(x+3,yy),(x+w-3,yy),1)
            elif style in ('lake','mirrorlake'):
                pygame.draw.ellipse(surf,(47,87,100),(x,y,w,h)); pygame.draw.ellipse(surf,(118,186,192),(x,y,w,h),1)
            elif style in ('hospital','hospitalroom'):
                pygame.draw.rect(surf,(61,78,101),(x,y,w,h),border_radius=3); pygame.draw.rect(surf,(151,185,195),(x,y,w,h),1,border_radius=3)
            elif style in ('theatre','stage'):
                pygame.draw.rect(surf,(63,31,57),(x,y,w,h),border_radius=3); pygame.draw.rect(surf,(192,103,140),(x,y,w,h),1,border_radius=3)
            elif style in ('house','bedroom','attic'):
                pygame.draw.rect(surf,(54,45,57),(x,y,w,h),border_radius=3); pygame.draw.rect(surf,(178,137,158),(x,y,w,h),1,border_radius=3)
            else:
                pygame.draw.rect(surf,(9,13,29),(x,y,w,h),border_radius=3); pygame.draw.rect(surf,p['line'],(x,y,w,h),1,border_radius=3)
        # Exit marker shows its actual side; this is not always an east-facing door.
        d=data['door']; side=data['exit']
        if side:
            if side in ('left','right'):
                x=2 if side=='left' else WIDTH-24
                pygame.draw.rect(surf,(6,9,22),(x,d[1]-38,22,76),border_radius=3)
                pygame.draw.rect(surf,p['glow'],(x,d[1]-38,22,76),2,border_radius=3)
                for yy in range(d[1]-28,d[1]+29,14): pygame.draw.line(surf,p['line'],(x+4,yy),(x+18,yy),1)
            else:
                y=2 if side=='up' else HEIGHT-24
                pygame.draw.rect(surf,(6,9,22),(d[0]-38,y,76,22),border_radius=3)
                pygame.draw.rect(surf,p['glow'],(d[0]-38,y,76,22),2,border_radius=3)
                for xx in range(d[0]-28,d[0]+29,14): pygame.draw.line(surf,p['line'],(xx,y+4),(xx,y+18),1)
        return surf

    def show_story_hint(self, text, duration=1.8):
        self.hint_text=text; self.hint_timer=duration

    def finish_dialogue(self):
        tag=self.dialogue_tag
        Game.finish_dialogue(self)
        if tag=='clear_scene':
            self.state['clear']=True
            self.audio.play_sfx('gate')
            self.show_story_hint('Il passaggio cambia forma. Cerca la soglia illuminata.',2.0)
        elif tag=='found_key':
            self.state['clear']=True
            item = 'Chiave della torre' if 'chiave_carrozza' in self.inventory else 'Indizio S-17'
            self.audio.play_sfx('pickup')
            self.show_story_hint(f'Oggetto ottenuto: {item}. Esplora e raggiungi l uscita.', 2.2)
        elif tag=='talk_complete':
            self.state['talked']=True
        elif tag=='start_chase':
            self.state['started']=True; self.state['progress']=0; self.npc_pos=list(self.scene['route'][0])
            self.show_story_hint('Raggiungi la figura prima che il treno cambi binario.',2.0)
        elif tag=='start_stealth':
            self.state['started']=True; self.state['progress']=0; self.state['last_checkpoint']=tuple(self.player)
            self.show_story_hint('La luce scandisce il tunnel. Aspetta che passi, poi attraversa le ombre.',2.4)
        elif tag=='start_memory_walk':
            self.state['started']=True; self.state['progress']=0
            self.show_story_hint('Cammina dentro il ricordo: le scene si attiveranno da sole.',2.0)
        elif tag=='start_tidal':
            self.state['started']=True; self.state['progress']=0
            self.show_story_hint('Avanza durante la bassa marea, riconoscibile dalla superficie che si ritira.',2.0)
        elif tag=='open_choice':
            self.choice_pending=True
        elif tag=='start_rhythm':
            self.rhythm_active=True; self.rhythm_clock=0.0; self.rhythm_hits=0
        elif tag=='start_battle':
            self.start_story_battle(self.scene['battle'])
        elif tag=='battle_win_end':
            self.state['clear']=True
            self.audio.play_sfx('gate')
            self.show_story_hint('Non hai vinto contro una persona. Hai cambiato il modo di ascoltare.',2.2)
        elif tag=='retry_battle':
            self.start_story_battle(self.scene['battle'])
        elif tag=='final_choice_pending':
            self.choice_pending=True
        elif tag=='complete_ending':
            self.ending=True
            self.audio.play_sfx('final')

    def handle_event(self,event):
        if event.type==pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type!=pygame.KEYDOWN: return
        key=event.key
        if key==pygame.K_ESCAPE:
            pygame.quit(); sys.exit()
        if key==pygame.K_m:
            self.audio.toggle_mute(); self.show_story_hint('Audio attivato' if not self.audio.muted else 'Audio disattivato'); return
        if not self.started:
            if key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_e,pygame.K_z): self.begin_campaign()
            return
        if self.ending:
            if key in (pygame.K_RETURN,pygame.K_SPACE): self.__init__()
            return
        if self.dialogue:
            if key in (pygame.K_e,pygame.K_z,pygame.K_RETURN,pygame.K_SPACE): self.advance_dialogue()
            return
        if self.choice_pending:
            if key in (pygame.K_1,pygame.K_2,pygame.K_3): self.resolve_choice(key-pygame.K_0)
            return
        if self.battle_active:
            if key in (pygame.K_e,pygame.K_z,pygame.K_RETURN,pygame.K_SPACE): self.story_battle_action()
            return
        if self.rhythm_active:
            if key in (pygame.K_e,pygame.K_z,pygame.K_RETURN,pygame.K_SPACE): self.tap_rhythm()
            return
        if key in (pygame.K_e,pygame.K_z,pygame.K_RETURN,pygame.K_SPACE): self.interact_story()

    def resolve_choice(self,choice):
        data=self.scene; st=self.state
        conversation = data['task']=='conversation'
        stage = st.get('conversation_stage',1)
        opts = data.get('second_options',data['options']) if conversation and stage >= 2 else data['options']
        idx=clamp(choice-1,0,len(opts)-1)
        self.choice_pending=False
        label,explain=opts[idx]
        if conversation and stage == 1:
            self.story_choices[self.scene_id+'_first']=idx+1
            st['conversation_stage']=2
            self.start_dialogue(data['responses'][idx],'open_choice')
            return
        if conversation and stage >= 2:
            self.story_choices[self.scene_id]=idx+1
            result=list(data['second_results'][idx])
            first=self.story_choices.get(self.scene_id+'_first',1)
            if self.scene_id=='dining' and first==3:
                result.append(('VOCE','Hai chiesto di restare. Il ricordo non ti punisce per averlo desiderato, ma non lascia che il desiderio diventi un contratto.'))
            self.start_dialogue(result,'clear_scene')
            return
        self.story_choices[self.scene_id]=idx+1
        if self.scene_id=='witness':
            self.story_choices['final']=idx+1
            endings=[
                [('IL TESTIMONE','Allora vengo con te. Non come una sentenza: come una parte della tua storia.'),('VOCE','Non hai liberato qualcuno da una gabbia. Hai aperto una porta che tenevi chiusa dentro di te.')],
                [('IL TESTIMONE','Non mi cancelli. Smetti soltanto di chiedermi di vivere al posto tuo.'),('VOCE','Il ricordo resta, ma non deve piu occupare ogni stanza del presente.')],
                [('IL TESTIMONE','Non credevo che saresti rimasto ad ascoltare.'),('VOCE','Questa volta non scappi da quello che senti e non gli consegni le chiavi. Resti, poi fai un passo.')]
            ]
            final_line = [
                'Hai portato con te il ricordo, senza trasformarlo in una condanna.',
                'Hai lasciato andare la punizione, non la persona che e stata importante.',
                'Hai scelto di ascoltarti senza lasciare che una sola emozione decida per te.'
            ][idx]
            market_line = [
                'Hai scelto i fatti anche quando non ti offrivano un finale perfetto.',
                'Hai scoperto che prendersi ogni colpa non e la stessa cosa che assumersi la propria parte.',
                'Hai provato a scappare, ma alla fine sei rimasto abbastanza a lungo per ascoltare.'
            ][self.story_choices.get('market', 1) - 1]
            library_line = [
                'Hai dato un nome alla paura che nascondevi.',
                'Hai riconosciuto che voler bene non concede il diritto di decidere per l’altra persona.',
                'Hai accettato di non sapere tutto, senza inventare risposte al posto degli altri.'
            ][self.story_choices.get('library', 3) - 1]
            dining_line = [
                'Hai chiesto scusa per il tuo silenzio, senza chiedere che il passato fosse cancellato.',
                'Hai detto che Neri ti e mancata, senza trasformare la nostalgia in una richiesta.',
                'Hai ammesso di aver voluto che restasse, e hai lasciato che la sua scelta fosse sua.'
            ][self.story_choices.get('dining', 2) - 1]
            self.story_ending = [final_line, market_line, library_line, dining_line,
                'Neri non era prigioniera. Eri tu ad essere rimasto alla banchina. Ora il treno puo restare un ricordo, non una destinazione.']
            self.start_dialogue(endings[idx],'complete_ending')
            return
        if self.scene_id=='market':
            result=[('ADA',"Lo scambio e fatto. Non hai comprato una vita alternativa: hai scelto quale verita portare con te."),('VOCE',("Hai scelto la verita. Il rimorso non sparisce, ma smette di essere l’unica voce nella stanza." if idx==0 else "Hai scelto il rimorso. E pesante, ma per la prima volta ti accorgi che stai portando anche cose che non erano tue." if idx==1 else "Hai scelto la fuga. Per un istante funziona. Poi la melodia della stazione ti raggiunge comunque."))]
        elif self.scene_id=='lobby':
            result=[('CAPOCOMICA', ["La maschera dell’aiuto non ti rende debole. Ti rende visibile.","La rabbia ha una ragione, ma non puo essere l’unica a parlare.","La maschera resta sul viso. Non ti giudico. Ma il palco non puo diventare casa tua."][idx]),('VOCE','Il sipario si muove anche se nessuno lo tocca. Sul palco qualcuno sta aspettando la tua parte.')]
        elif self.scene_id=='childroom':
            result=[('RICORDO',["Lo dici ad alta voce e la frase smette di essere una condanna segreta.","La difesa era vera, ma non era tutta la verita.","Non sapere e diverso dal fingere di sapere. Il ricordo si lascia guardare."][idx]),('VOCE','La soffitta si apre. Non perche hai trovato la risposta giusta, ma perche hai smesso di recitare una sola risposta.')]
        elif self.scene_id=='library':
            result=[('LUMA',["La paura e una spiegazione, non una vergogna.","La cura per qualcuno non obbliga a chiedere che resti.","Non sapere e una risposta onesta, se smetti di usarla per scappare."][idx]),('VOCE','La frase incompleta resta sul leggio. Per la prima volta, non provi a correggerla.')]
        else:
            result=[(data['npc'],explain)]
        self.start_dialogue(result,'clear_scene')

    def interact_story(self):
        data=self.scene; st=self.state; px,py=self.player
        cand=[(distance((px,py),self.npc_pos),'npc',None)]
        for i,prop in enumerate(data['props']): cand.append((distance((px,py),prop['pos']),'prop',i))
        nearby=[v for v in cand if v[0]<62]
        if not nearby:
            self.show_story_hint('Avvicinati alla persona o all’elemento luminoso e premi E.',1.2); return
        _,kind,idx=min(nearby,key=lambda v:v[0])
        task=data['task']
        if kind=='npc':
            if task in ('battle','final_battle'):
                if st['clear']:
                    self.show_story_hint('Questo ricordo e stato affrontato. La soglia ora e aperta.', 1.5); return
                if not st['started']:
                    st['started']=True
                    self.start_dialogue(data['npc_lines'],'start_battle')
                else: self.show_story_hint('Lo scontro continua a chiederti qualcosa di diverso.');
                return
            if task=='choice':
                if st['clear']:
                    chosen=self.story_choices.get(self.scene_id,1)
                    self.start_dialogue([(data['npc'],'Hai gia scelto. Non devi difendere la tua risposta per meritarti di andare avanti.')])
                elif not st['talked']:
                    st['talked']=True; self.start_dialogue(data['npc_lines'],'open_choice')
                else: self.choice_pending=True
                return
            if task=='conversation':
                if st['clear']:
                    self.start_dialogue([(data['npc'],'Abbiamo gia affrontato questa conversazione. Non devi ripeterla per renderla perfetta.')])
                elif not st['talked']:
                    st['talked']=True; self.start_dialogue(data['npc_lines'],'open_choice')
                else:
                    self.choice_pending=True
                return
            if task in ('chase','stealth','memory_walk','tidal'):
                tag={'chase':'start_chase','stealth':'start_stealth','memory_walk':'start_memory_walk','tidal':'start_tidal'}[task]
                if not st['started']:
                    self.start_dialogue(data['npc_lines'],tag)
                else:
                    hints={'chase':'Segui la figura: si sposta quando ti avvicini.','stealth':'Aspetta che la luce attraversi il corridoio prima di passare.','memory_walk':'Avvicinati al prossimo frammento del ricordo.','tidal':'La marea scende a intervalli: attraversa quando l acqua si ritira.'}
                    self.show_story_hint(hints[task],1.5)
                return
            if task=='two_step':
                if not st['talked']:
                    st['talked']=True; self.start_dialogue(data['npc_lines'],'talk_complete')
                else: self.show_story_hint('La persona ti ha gia detto cosa sa. Guarda l’ambiente, non cercare un altro inventario.')
                return
            if task in ('runes','route'):
                if not st['started']:
                    st['started']=True; self.start_dialogue(data['npc_lines'])
                    self.show_story_hint('Segui il percorso indicato nel dialogo.',2.3)
                else: self.start_dialogue([(data['npc'],'Non serve correre. Segui il prossimo segnale sul pavimento.')])
                return
            if task=='sequence':
                if not st['talked']:
                    st['talked']=True; self.start_dialogue(data['npc_lines'])
                else: self.show_story_hint('Prova gli elementi nel giusto ordine: E vicino al simbolo.',1.5)
                return
            if task=='rhythm':
                if not st['started']:
                    st['started']=True; self.start_dialogue(data['npc_lines'],'start_rhythm')
                else: self.show_story_hint('Ascolta il battito e premi E quando l’anello si illumina.',1.5)
                return
            if task=='memory':
                self.start_dialogue(data['npc_lines'])
                return
            if task=='search_room':
                self.start_dialogue(data['npc_lines'])
                return
        else:
            prop=data['props'][idx]
            if prop.get('side_room'):
                if 'chiave_carrozza' in self.inventory:
                    self.show_story_hint('Hai gia la chiave della torre. Torna alla soglia del treno.', 1.8)
                elif not st.get('clear'):
                    self.show_story_hint('Prima segui il Capocorsa fino alla fine della carrozza.', 1.6)
                else:
                    self.side_return = (self.scene_id, (float(px), float(py)))
                    self.audio.play_sfx('gate')
                    self.enter_scene(prop['side_room'])
                return
            if task == 'search_room':
                if idx in st['props']:
                    self.show_story_hint('Hai gia controllato qui. Cerca un altro punto della carrozza.', 1.2); return
                st['props'].add(idx)
                key_item = prop.get('key_item')
                if key_item:
                    self.inventory.add(key_item)
                    self.start_dialogue(prop['lines'], 'found_key')
                else:
                    self.start_dialogue(prop['lines'])
                return
            if idx in st['props']:
                self.show_story_hint('Questo ricordo non ha altro da aggiungere, per ora.'); return
            if task=='two_step' and not st['talked']:
                self.show_story_hint('Prima parla con Pip. Non tutto si apre con un oggetto.',1.5); return
            if task=='sequence':
                expected=data['order'][st['progress']] if st['progress']<len(data['order']) else idx
                if idx!=expected:
                    st['progress']=0; st['props'].clear(); self.audio.play_sfx('wrong')
                    self.start_dialogue([('VOCE','L’ordine non torna. La memoria si riavvolge, ma non cancella quello che hai capito.')]); return
                st['props'].add(idx); st['progress']+=1
                lines=prop['lines']
                if st['progress']>=len(data['order']): lines=lines+[('VOCE','Le frasi si ricompongono. Non sono perfette. Sono finalmente tue.')]
                self.start_dialogue(lines,'clear_scene' if st['progress']>=len(data['order']) else None)
                return
            st['props'].add(idx)
            tag='clear_scene' if task in ('two_step','memory') else None
            self.start_dialogue(prop['lines'],tag)
            return

    def tap_rhythm(self):
        # Each beat lasts 1.8 seconds; the bright pulse is a generous 0.48-second window.
        phase=self.rhythm_clock%1.8
        if 0.58<=phase<=1.08:
            self.rhythm_hits+=1; self.audio.play_sfx('pickup')
            self.show_story_hint(f'Battito trovato: {self.rhythm_hits}/3',0.85)
            if self.rhythm_hits>=3:
                self.rhythm_active=False
                self.start_dialogue([('IL PENDOLO','Il tempo non e tornato indietro. Sei tu che hai smesso di chiederglielo.'),('VOCE','L’orologio riprende a muoversi in avanti.')],'clear_scene')
        else:
            self.rhythm_hits=0; self.audio.play_sfx('wrong'); self.show_story_hint('Troppo presto o troppo tardi: segui il lampo e riprova.',1.1)

    def move_story(self,dx,dy):
        data=self.scene; x,y=self.player; nx=x+dx; ny=y+dy
        # Doors use different sides; the scene is only traversable through walkable floor.
        nx=clamp(nx,3,WIDTH-3); ny=clamp(ny,3,HEIGHT-3)
        if self.walkable(nx,ny): pass
        else:
            canx=self.walkable(nx,y); cany=self.walkable(x,ny)
            if canx: ny=y
            elif cany: nx=x
            else: nx,ny=x,y
        self.player=[nx,ny]
        if abs(dx)+abs(dy)>0: self.walk_time+=math.hypot(dx,dy)*0.1
        side=data['exit']; door=data['door']
        at_door=False
        if side=='right' and nx>=WIDTH-10 and abs(ny-door[1])<50: at_door=True
        elif side=='left' and nx<=10 and abs(ny-door[1])<50: at_door=True
        elif side=='up' and ny<=10 and abs(nx-door[0])<50: at_door=True
        elif side=='down' and ny>=HEIGHT-10 and abs(nx-door[0])<50: at_door=True
        if at_door and side:
            if self.state['clear']:
                if self.scene_id == 'tram' and 'chiave_carrozza' not in self.inventory:
                    self.player = ([30.0, float(door[1])] if side == 'left' else
                                   [WIDTH-30.0, float(door[1])] if side == 'right' else
                                   [float(door[0]), 28.0] if side == 'up' else
                                   [float(door[0]), HEIGHT-28.0])
                    self.show_story_hint('La torre e chiusa. Cerca la porta della carrozza laterale e segui l indizio fino alla chiave.', 2.4)
                elif data.get('is_side_room') and data.get('next'):
                    self.audio.play_sfx('gate'); self.enter_scene(data['next'])
                elif data.get('is_side_room') and self.side_return:
                    return_scene, return_pos = self.side_return
                    self.side_return = None
                    self.audio.play_sfx('gate')
                    self.enter_scene(return_scene, show_intro=False)
                    self.player = [float(return_pos[0]), float(return_pos[1])]
                    self.show_story_hint('Sei tornato alla carrozza principale. La chiave e al sicuro.', 1.8)
                elif data['next']:
                    self.audio.play_sfx('gate'); self.enter_scene(data['next'])
            else:
                self.player=[clamp(nx,24,WIDTH-24),clamp(ny,24,HEIGHT-24)]
                self.show_story_hint(self.exit_hint(),1.4)

    def walkable(self,x,y):
        point=(int(x),int(y)); data=self.scene
        if not any(pygame.Rect(*r).collidepoint(point) for r in data['floors']): return False
        for r in data['blocks']:
            if pygame.Rect(*r).inflate(6,6).collidepoint(point): return False
        return True

    def exit_hint(self):
        task=self.scene['task']
        if task=='two_step': return 'Parla con Pip e poi leggi il tabellone.'
        if task=='runes': return 'La via si apre quando attraversi le luci nell’ordine giusto.'
        if task=='sequence': return 'La porta resta chiusa: la frase o la melodia non e ancora completa.'
        if task=='rhythm': return 'Il pendolo aspetta tre battiti presi al momento giusto.'
        if task=='route': return 'Attraversa il percorso luminoso, non cercare un oggetto da raccogliere.'
        if task=='battle': return 'La soglia aspetta che lo scontro interiore cambi.'
        if task=='final_battle': return 'Ascolta il Testimone: la regola cambia a ogni fase.'
        if task=='choice': return 'Parla, poi scegli: la decisione si farà sentire più avanti.'
        if task=='conversation': return 'Questa conversazione ha due passaggi: rispondi anche alla seconda domanda.'
        if task=='chase': return 'Segui il Capocorsa. Poi esplora la carrozza laterale: la torre richiede una chiave.'
        if task=='stealth': return 'Usa le rientranze e attraversa dopo che la luce è passata.'
        if task=='memory_walk': return 'Attraversa le scene del ricordo; ogni punto attiva un frammento di storia.'
        if task=='tidal': return 'Attraversa le passerelle solo quando la marea è bassa.'
        if task=='search_room': return 'Esamina ogni zona con E. Cerca il punto che contiene l indizio o la chiave.'
        if task=='rhythm': return 'Tre battiti, ma non devi essere perfetto: segui il lampo e riprova.'
        return 'Il passaggio non è ancora pronto.'

    def update(self,dt,keys):
        self.story_t+=dt
        for part in self.particles: part.update(dt,self.room)
        self.room_title_timer=max(0,self.room_title_timer-dt)
        self.flash_timer=max(0,self.flash_timer-dt)
        self.hint_timer=max(0,self.hint_timer-dt)
        self.battle_flash=max(0,self.battle_flash-dt)
        if self.dialogue:
            line = self.dialogue[self.dialogue_index][1]
            self.dialogue_chars = min(len(line), self.dialogue_chars + self.dialogue_speed * dt)
            return
        if not self.started or self.ending or self.choice_pending: return
        if self.battle_active:
            self.update_story_battle(dt,keys); return
        if self.rhythm_active:
            self.rhythm_clock+=dt; return
        dx=(1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0)-(1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        dy=(1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0)-(1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        if dx or dy:
            mag=math.hypot(dx,dy); speed=220 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 158
            if dx: self.facing=(dx,0)
            elif dy: self.facing=(0,dy)
            self.move_story(dx/mag*speed*dt,dy/mag*speed*dt)
            self.step_sound_timer-=dt
            if self.step_sound_timer<=0: self.audio.play_sfx('step'); self.step_sound_timer=0.31
        else: self.step_sound_timer=min(self.step_sound_timer,0.05)
        # Walking puzzles, triggers, and safe-zone traversal are spatial instead of inventory-based.
        if self.scene['task'] in ('runes','route','memory_walk','tidal') and self.state['started'] and not self.state['clear']:
            self.update_route_task()
        elif self.scene['task']=='chase' and self.state['started'] and not self.state['clear']:
            self.update_chase_task(dt)
        elif self.scene['task']=='stealth' and self.state['started'] and not self.state['clear']:
            self.update_stealth_task()
        elif self.scene['task']=='memory' and not self.state['clear'] and distance(self.player,self.scene['props'][0]['pos'])<32:
            if 0 not in self.state['props']:
                self.state['props'].add(0); self.start_dialogue(self.scene['props'][0]['lines'],'clear_scene')

    def update_route_task(self):
        st=self.state; data=self.scene; pts=data['route']; task=data['task']
        if st['progress']>=len(pts): return
        x,y=pts[st['progress']]
        close=distance(self.player,(x,y))<31
        if not close: return
        if task=='tidal':
            phase=self.story_t%3.6
            if phase>2.25:
                self.show_story_hint('L acqua torna alta. Aspetta la bassa marea per passare.',0.65); return
        st['progress']+=1; self.audio.play_sfx('pickup'); self.flash_timer=0.11
        if task=='memory_walk':
            events=data.get('events',[])
            lines=events[st['progress']-1] if st['progress']-1<len(events) else [('VOCE','Il ricordo si lascia attraversare. Non devi portarlo tutto in una volta.')]
            self.start_dialogue(lines,'clear_scene' if st['progress']>=len(pts) else None)
            return
        if st['progress']>=len(pts):
            endings={ 'garden':[('NIA','Le luci si spengono, ma la sequenza resta nei tuoi passi.'),('VOCE','Il vetro non si e riparato. E diventato trasparente.')],
             'shore':[('BARCAIOLO','Hai attraversato il lago senza sapere cosa c’era sull’altra riva.'),('VOCE','La paura non e sparita. Questa volta non ha deciso al posto tuo.')],
             'platform_final':[('VOCE','La banchina si ricompone sotto i tuoi passi. La figura non scappa quando ti avvicini.')],
             'island':[('BARCAIOLO','Hai attraversato mentre l acqua lasciava spazio. Non hai vinto contro la marea.'),('VOCE','Hai imparato a non chiamare ostacolo ogni cosa che non puoi controllare.')]} 
            self.start_dialogue(endings.get(self.scene_id,[('VOCE','Il percorso e completo. Ora puoi proseguire.')]),'clear_scene')
        else:
            self.state['last_checkpoint']=(x,y)
            if task=='tidal': self.show_story_hint(f'Bassa marea: {st["progress"]}/{len(pts)}',0.8)
            else: self.show_story_hint(f'Percorso: {st["progress"]}/{len(pts)}',0.8)

    def update_chase_task(self,dt):
        st=self.state; data=self.scene; pts=data['route']
        if st['progress']>=len(pts): return
        if st.get('chase_moving'):
            st['chase_elapsed']=st.get('chase_elapsed',0.0)+dt
            a=st.get('chase_from',tuple(self.npc_pos)); target=st.get('chase_target',tuple(self.npc_pos))
            f=min(1.0,st['chase_elapsed']/0.85)
            self.npc_pos=[a[0]+(target[0]-a[0])*f,a[1]+(target[1]-a[1])*f]
            if f>=1.0: st['chase_moving']=False; self.npc_pos=list(target)
            return
        if distance(self.player,self.npc_pos)<78:
            st['progress']+=1; self.audio.play_sfx('pickup'); self.flash_timer=0.12
            if st['progress']>=len(pts):
                self.start_dialogue([('CAPOCORSA','Eccola. Non e una richiesta di aiuto: e una registrazione che avevi paura di ascoltare.'),('VOCE','La carrozza rallenta. Per la prima volta, smetti di inseguire una versione alternativa del viaggio e ascolti quella che e accaduta.')],'clear_scene')
            else:
                st['chase_from']=tuple(self.npc_pos); st['chase_target']=tuple(pts[st['progress']]); st['chase_elapsed']=0.0; st['chase_moving']=True
                self.show_story_hint('La figura passa alla carrozza successiva. Continua a seguirla.',1.2)

    def update_stealth_task(self):
        st=self.state; data=self.scene; pts=data['route']
        phase=self.story_t%2.8; scanning=phase>2.02
        beamx=480+math.sin(self.story_t*0.88)*335
        beamy=315+math.sin(self.story_t*1.17)*58
        cycle=int(self.story_t/2.8)
        if scanning and st.get('stealth_cycle')!=cycle and abs(self.player[0]-beamx)<55 and abs(self.player[1]-beamy)<62:
            st['stealth_cycle']=cycle
            checkpoint=st.get('last_checkpoint')
            self.player=list(checkpoint if checkpoint else data['spawn'])
            self.audio.play_sfx('wrong'); self.flash_timer=0.16
            self.show_story_hint('La luce ti ha trovato. Torna all ombra e riprova quando passa.',1.2)
        if st['progress']<len(pts) and distance(self.player,pts[st['progress']])<30:
            # The alcove is safe only once the sweeping voice/light has passed.
            if scanning: self.show_story_hint('Aspetta che la luce passi: questa non e ancora un ombra sicura.',0.7); return
            x,y=pts[st['progress']]; st['progress']+=1; st['last_checkpoint']=(x,y)
            self.audio.play_sfx('pickup'); self.flash_timer=0.1
            if st['progress']>=len(pts):
                self.start_dialogue([('RAGAZZA','Le voci sono ancora qui, ma non stai piu correndo dietro a ogni versione.'),('VOCE','Hai lasciato il sottopassaggio senza trasformare una frase sentita a meta in una condanna.')],'clear_scene')
            else: self.show_story_hint(f'Ombra raggiunta: {st["progress"]}/{len(pts)}. La luce sta tornando.',0.9)

    def start_story_battle(self, kind):
        # The four named gatekeepers scale with the campaign. The final encounter is a special memory mechanic, not a fifth boss.
        try:
            rank = 1 + sum(1 for key in SCENE_ORDER[:SCENE_ORDER.index(self.scene_id)]
                           if STORY_AREAS[key]['task'] in ('battle', 'final_battle'))
        except (ValueError, KeyError):
            rank = 1
        stage_info = BOSS_STAGE_SCENES.get(self.scene_id)
        # Boss health is deliberately tuned for multi-cycle fights, not four quick taps.
        max_hp = 25 + int(rank * 2.6) if stage_info else (40 if kind == 'witness' else 25 + int(rank * 2.6))
        max_player_hp = max(12, 22 - int(rank * 0.7))
        color = stage_info['color'] if stage_info else BATTLE_NAMES.get(kind, ('', '', (124, 208, 224)))[2]
        self.battle_active = True
        self.battle_flash = 0.35
        self.battle = {
            'type': kind, 'rank': rank, 'stage_info': stage_info, 'color': color,
            'tick': 0.0, 'turn': ('enemy' if kind == 'witness' else 'player'), 'attack_clock': 0.0, 'enemy_clock': 0.0,
            'hp': max_player_hp, 'max_player_hp': max_player_hp,
            'boss_hp': max_hp, 'max_boss_hp': max_hp, 'rounds': 0,
            'heart': [480.0, 368.0], 'bullets': [], 'spawn_clock': 0.0,
            'spawn_count': 0, 'hit_cd': 0.0, 'flash': 0.0,
            'combat_phase': 0, 'message': 'TOCCA A TE: PREMI E QUANDO LA LUCE È VICINA AL CENTRO',
            'pattern': 0, 'last_attack': None, 'damage_text': '', 'damage_timer': 0.0, 'special_memory': (kind == 'witness'),
            'turn_result': '', 'turn_result_timer': 0.0,
        }
        self.audio.play_sfx('talk')
        if kind == 'witness':
            guide = 'NON È UN BOSS: NON ATTACCARE. LASCIA CHE IL FRAMMENTO DI MEMORIA TI RAGGIUNGA. OGNI IMPATTO LO INDEBOLISCE.'
        elif stage_info:
            guide = f"INCONTRO {stage_info['stage']}/4 — {stage_info['name']}. ATTACCA CON E, POI SCHIVA CON WASD/FRECCE."
        else:
            guide = 'TURNO TUO: E QUANDO IL SEGNALE È VICINO AL CENTRO. TURNO NEMICO: SCHIVA CON WASD/FRECCE; SHIFT SCATTO.'
        self.show_story_hint(guide, 4.2)

    def _battle_pattern_name(self, b):
        return ('PIOGGIA', 'MIRINO', 'MURO', 'SPIRALE', 'CROCE')[b['pattern'] % 5]

    def _battle_add_bullet(self, b, x, y, vx, vy, radius=7):
        b['bullets'].append({'x': float(x), 'y': float(y), 'vx': float(vx), 'vy': float(vy),
                             'r': radius, 'life': 5.0})

    def _battle_spawn_pattern(self, b):
        x, y = b['heart']
        rank = b['rank']
        phase_boost = b['combat_phase']
        speed = 150 + rank * 8 + phase_boost * 24
        stage_no = b['stage_info']['stage'] if b.get('stage_info') else 0
        if b.get('special_memory'):
            sources = [(480, 236), (270, 358), (690, 358), (480, 476)]
            sx, sy = sources[b['spawn_count'] % len(sources)]
            dx, dy = x - sx, y - sy
            mag = max(1.0, math.hypot(dx, dy))
            v = 112 + min(18, b['spawn_count'] * 3)
            self._battle_add_bullet(b, sx, sy, dx / mag * v, dy / mag * v, 9)
            b['bullets'][-1]['memory'] = True
            b['spawn_count'] += 1
            return
        # Each emotional stage changes the pressure, not just the boss's name.
        if stage_no == 2:      # Rabbia: faster, forceful volleys
            speed *= 1.14
        elif stage_no == 4:    # Depressione: slower waves that occupy the arena longer
            speed *= 0.88
        elif stage_no == 5:    # Accettazione: every phase becomes more direct
            speed *= 1.06 + phase_boost * 0.08
        n = b['spawn_count']
        pattern = b['pattern'] % 5
        xs = (305, 392, 480, 568, 655)
        if pattern == 0:  # ONDA ORIZZONTALE: una fascia sicura viene annunciata prima della raffica
            ys = (258, 302, 346, 390, 434, 468)
            gap = (b['rounds'] + n // 2 + rank) % len(ys)
            b['safe_y'] = ys[gap]
            from_left = (n + b['rounds']) % 2 == 0
            sx = 266 if from_left else 694
            vx = speed * (1.0 if from_left else -1.0)
            for i, sy in enumerate(ys):
                if i != gap:
                    self._battle_add_bullet(b, sx, sy, vx * (1.0 + 0.035 * (i % 2)), 0, 7)
        elif pattern == 1:  # MIRINO: proiettili diretti verso la posizione del cuore al momento del lancio
            sx = 315 + ((n * 73 + b['rounds'] * 41) % 330)
            source = (sx, 242 if n % 2 == 0 else 470)
            dx, dy = x - source[0], y - source[1]
            mag = max(1.0, math.hypot(dx, dy))
            v = speed + 18
            self._battle_add_bullet(b, source[0], source[1], dx / mag * v, dy / mag * v, 8)
            if (rank >= 4 or stage_no == 3) and (n + b['rounds']) % 2 == 0:
                sx2 = 655 - (sx - 315)
                dx2, dy2 = x - sx2, y - source[1]
                mag2 = max(1.0, math.hypot(dx2, dy2))
                self._battle_add_bullet(b, sx2, source[1], dx2 / mag2 * (v * 0.88), dy2 / mag2 * (v * 0.88), 7)
        elif pattern == 2:  # MURO: una fila attraversa l'arena con un varco ben visibile
            gap = (n + b['rounds'] + rank) % 6
            ys = (254, 296, 338, 380, 422, 464)
            from_left = (n + b['rounds']) % 2 == 0
            sx = 268 if from_left else 692
            vx = speed * (1 if from_left else -1)
            for i, sy in enumerate(ys):
                if i != gap:
                    self._battle_add_bullet(b, sx, sy, vx, 0, 7)
        elif pattern == 3:  # SPIRALE: due raggi rotanti escono dal centro
            angle = n * (0.51 + rank * 0.012) + b['rounds'] * 0.83
            for offset in (0, math.pi):
                a = angle + offset
                self._battle_add_bullet(b, 480, 358,
                    math.cos(a) * (speed * 0.82), math.sin(a) * (speed * 0.82), 7)
        else:  # CROCE: diagonali alternate, densità crescente nelle fasi avanzate
            shift = (n * 29 + b['rounds'] * 17) % 78
            for i, sx in enumerate((322 + shift, 470 + shift // 2, 618 - shift // 2)):
                direction = 1 if (i + n + b['rounds']) % 2 == 0 else -1
                self._battle_add_bullet(b, sx, 241 if direction > 0 else 477,
                    ((x - sx) / 430.0) * (speed * 0.42), direction * speed, 7)
                if rank >= 6 and i == 1:
                    self._battle_add_bullet(b, 268 if n % 2 == 0 else 692,
                        280 + ((n * 47) % 155), speed * (1 if n % 2 == 0 else -1), 0, 6)

        # Later stages layer a signature threat on top of the base pattern.
        if stage_no == 2 and n % 2 == 0 and pattern not in (2, 4):
            # Anger: a fast horizontal slash punishes camping in one lane.
            left_to_right = (n + b['rounds']) % 2 == 0
            self._battle_add_bullet(b, 266 if left_to_right else 694,
                278 + ((n * 43 + b['rounds'] * 19) % 160),
                speed * (1 if left_to_right else -1), 0, 6)
        if stage_no == 4 and n % 2 == 1:
            # Depression: an extra slow descending wave reduces the time spent idle.
            self._battle_add_bullet(b, 355 + ((n * 61) % 250), 238,
                                    0, speed * 0.72, 6)
        if stage_no == 5 and phase_boost >= 1:
            # Acceptance: after the reveal begins, each pattern also sends an echo
            # aimed at the soul's position when the volley starts.
            dx, dy = x - 480, y - 358
            mag = max(1.0, math.hypot(dx, dy))
            self._battle_add_bullet(b, 480, 358, dx / mag * speed * 0.74,
                                    dy / mag * speed * 0.74, 6)
        b['spawn_count'] += 1

    def update_story_battle(self, dt, keys):
        b = self.battle
        if not b:
            return
        b['tick'] += dt
        b['hit_cd'] = max(0.0, b['hit_cd'] - dt)
        b['flash'] = max(0.0, b['flash'] - dt)
        b['damage_timer'] = max(0.0, b['damage_timer'] - dt)
        b['turn_result_timer'] = max(0.0, b['turn_result_timer'] - dt)
        rank = b['rank']
        if b['turn'] == 'player':
            b['attack_clock'] += dt
            # The soul is kept in the arena during the timing attack; the marker sweeps
            # across a clear lane, just like a classic timed RPG attack.
            phase = 0.5 + 0.5 * math.sin(b['attack_clock'] * (2.15 + rank * 0.045) - math.pi / 2)
            b['marker_x'] = 320 + phase * 320
            return

        # Enemy turn: move the SOUL, then update deterministic bullet patterns.
        mx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        my = (1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0) - (1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        x, y = b['heart']
        if mx or my:
            mag = math.hypot(mx, my)
            speed = 238 + min(22, rank * 2)
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                speed *= 1.34
            x += mx / mag * speed * dt
            y += my / mag * speed * dt
        x = clamp(x, 276, 684)
        y = clamp(y, 247, 469)
        b['heart'] = [x, y]

        b['enemy_clock'] += dt
        # A warning beat makes even the hard patterns readable before the first volley.
        warning = 0.58
        interval = max(0.29, 0.66 - rank * 0.025 - b['combat_phase'] * 0.035)
        b['spawn_clock'] += dt
        if b['enemy_clock'] >= warning and (b['spawn_count'] == 0 or (not b.get('special_memory') and b['spawn_clock'] >= interval)):
            b['spawn_clock'] = 0.0
            self._battle_spawn_pattern(b)

        for bullet in b['bullets'][:]:
            bullet['x'] += bullet['vx'] * dt
            bullet['y'] += bullet['vy'] * dt
            bullet['life'] -= dt
            if (bullet['life'] <= 0 or bullet['x'] < 250 or bullet['x'] > 710
                    or bullet['y'] < 220 or bullet['y'] > 500):
                b['bullets'].remove(bullet)
                continue
            if b['hit_cd'] <= 0 and math.hypot(bullet['x'] - x, bullet['y'] - y) < bullet['r'] + 7:
                if b.get('special_memory') and bullet.get('memory'):
                    b['boss_hp'] = max(0, b['boss_hp'] - 10)
                    b['hp'] -= 1
                    b['damage_text'] = 'IL RICORDO TI ATTRAVERSA'
                    b['damage_timer'] = 1.0
                    b['hit_cd'] = 0.82
                    b['flash'] = 0.28
                    self.battle_flash = 0.2
                    self.audio.play_sfx('talk')
                    if bullet in b['bullets']:
                        b['bullets'].remove(bullet)
                    self.show_story_hint(f'NON SCHIVARE — LA FIGURA SI INDEBOLISCE: {b['boss_hp']}/{b['max_boss_hp']}', 1.0)
                    if b['boss_hp'] <= 0:
                        self.win_battle()
                        return
                    continue
                damage = 1
                b['hp'] -= damage
                b['hit_cd'] = 0.68
                b['flash'] = 0.19
                b['damage_text'] = f'-{damage} RESPIRO'
                b['damage_timer'] = 0.7
                self.battle_flash = 0.16
                self.audio.play_sfx('wrong')
                self.show_story_hint(f'COLPITO! RESPIRO {max(0, b["hp"])}/{b["max_player_hp"]}. CONTINUA A MUOVERTI.', 0.75)
                # Remove the bullet that hit so lingering overlap cannot drain the bar.
                if bullet in b['bullets']:
                    b['bullets'].remove(bullet)
                if b['hp'] <= 0:
                    name = (b['stage_info']['name'] if b['stage_info'] else BATTLE_NAMES.get(b['type'], ('L’AVVERSARIO',))[0])
                    self.battle_active = False
                    self.battle = None
                    self.start_dialogue([(name, 'Il colpo finale ti sorprende. La sequenza ricomincia, ma ora conosci il suo ritmo.'),
                                         ('VOCE', 'La battaglia riparte dall’inizio. Ogni attacco ha un segnale: guarda il campo prima di scegliere dove muoverti.')], 'retry_battle')
                    return

        # Enemy barrage ends only after its full turn: survive the pattern, not a single check.
        duration = 3.1 + rank * 0.17 + b['combat_phase'] * 0.32
        if b['stage_info'] and b['stage_info']['stage'] == 4:
            duration += 0.35  # the emptier, longer attack windows are part of this fight
        elif b['stage_info'] and b['stage_info']['stage'] == 5:
            duration += 0.25 + b['combat_phase'] * 0.25
        if b['enemy_clock'] >= duration:
            b['bullets'].clear()
            if b.get('special_memory'):
                b['turn'] = 'enemy'
                b['enemy_clock'] = 0.0
                b['spawn_clock'] = 0.0
                b['spawn_count'] = 0
                b['message'] = 'NON SCHIVARE IL RICORDO — LASCIA CHE TI RAGGIUNGA'
                b['turn_result'] = 'IL RICORDO TORNA, PIÙ VICINO'
                b['turn_result_timer'] = 0.8
            else:
                b['turn'] = 'player'
                b['attack_clock'] = 0.0
                b['message'] = 'TOCCA A TE — PREMI E VICINO AL CENTRO PER UN COLPO MIGLIORE'
                b['turn_result'] = 'IL NEMICO SI RITIRA — ATTACCA ORA'
                b['turn_result_timer'] = 1.0
                b['heart'] = [480.0, 368.0]
                self.audio.play_sfx('pickup')

    def damage_battle(self):
        # Backwards-compatible helper used by no single-pattern encounter anymore.
        if self.battle:
            self.battle['hp'] = max(0, self.battle['hp'] - 1)
            self.battle['flash'] = 0.18

    def story_battle_action(self):
        b = self.battle
        if not b:
            return
        if b.get('special_memory'):
            self.show_story_hint('NON ATTACCARE E NON SCHIVARE. LASCIA CHE IL FRAMMENTO TI RAGGIUNGA.', 1.3)
            return
        if b['turn'] != 'player':
            self.show_story_hint('ORA SCHIVA! L’attacco nemico non finisce finché non passa la raffica.', 1.1)
            return
        marker_x = b.get('marker_x', 480)
        accuracy = abs(marker_x - 480)
        if accuracy <= 18:
            damage = 3
            rating = 'PERFETTO!'
        elif accuracy <= 54:
            damage = 2
            rating = 'CENTRATO!'
        else:
            damage = 1
            rating = 'COLPO DEBOLE'
        b['boss_hp'] = max(0, b['boss_hp'] - damage)
        b['rounds'] += 1
        b['damage_text'] = f'-{damage} HP  ·  {rating}'
        b['damage_timer'] = 1.15
        self.audio.play_sfx('pickup')
        # Bosses acquire new patterns as their health falls. The final Acceptance fight has 3 phases.
        ratio = b['boss_hp'] / max(1, b['max_boss_hp'])
        new_phase = 0 if ratio > 0.66 else 1 if ratio > 0.33 else 2
        if b['stage_info'] is None and b['rank'] < 4:
            new_phase = 0 if ratio > 0.5 else 1
        if new_phase > b['combat_phase']:
            b['combat_phase'] = new_phase
            b['turn_result'] = ('FASE II — IL RITMO ACCELERA' if new_phase == 1 else 'FASE III — NESSUN VARCO GRATUITO')
            b['turn_result_timer'] = 1.35
            self.battle_flash = 0.22
        if b['boss_hp'] <= 0:
            self.win_battle()
            return
        b['turn'] = 'enemy'
        b['enemy_clock'] = 0.0
        b['spawn_clock'] = 0.0  # first volley waits for the complete telegraph beat
        b['spawn_count'] = 0
        b['pattern'] = (b['rounds'] + b['rank'] - 1 + b['combat_phase']) % 5
        b['bullets'] = []
        b['message'] = f"SCHIVA — {self._battle_pattern_name(b)}"
        b['heart'] = [480.0, 368.0]

    def answer_doubt(self,choice):
        b = self.battle
        if not b:
            return
        questions = (
            ('Non puoi sapere il futuro.', 2, 'Accettare l incertezza e una scelta reale; prevedere o fuggire non e una certezza.'),
            ('Che cosa sai davvero?', 1, 'I fatti sono cio che puoi verificare; paure e ipotesi possono sembrare vere, ma non sono prove.'),
            ('Che cosa puoi fare adesso?', 3, 'Puoi scegliere il prossimo passo; punirti o cancellare il passato non lo modifica.')
        )
        _, correct, explanation = questions[min(2, b['progress'])]
        if choice == correct:
            b['progress'] += 1
            self.audio.play_sfx('pickup')
            if b['progress'] >= 3:
                self.win_battle()
            else:
                self.show_story_hint(explanation, 2.2)
        else:
            self.audio.play_sfx('wrong')
            self.show_story_hint('Non perdi respiro per una risposta sbagliata. ' + explanation, 2.5)

    def win_battle(self):
        b = self.battle
        if not b:
            return
        kind = b['type']
        stage_info = b.get('stage_info')
        self.battle_active = False
        self.battle = None
        self.battle_flash = 0.4
        stage_lines = {
            1: [('IL PORTIERE', 'Non credere che questo significhi che sei pronto.'),
                ('VOCE', 'La porta si apre. Dietro, una luce tremola come il finestrino di un treno lontano. Neri potrebbe essere ancora più avanti.')],
            2: [('IL GUARDIANO', 'Non è finita. Se la trovi, non dire che non ti avevo avvertito.'),
                ('VOCE', 'La strada è libera. Dall’altra parte, un biglietto porta il nome di Neri e una destinazione che non riesci a leggere.')],
            3: [('IL MERCANTE', 'Il patto è rotto. Ma forse non ti serviva davvero.'),
                ('VOCE', 'Le promesse si dissolvono e lasciano un nuovo indizio. Ti sembra di essere sempre più vicino a Neri.')],
            4: [('LA SENTINELLA', 'Sei arrivato fin qui. E se lei non volesse vederti?'),
                ('VOCE', 'La porta alle tue spalle si chiude. Davanti, una figura ti aspetta in una stanza che sembra familiare.')],
            5: [('ACCETTAZIONE', 'Non ho sconfitto la mancanza. Ho smesso di chiederle di diventare un indirizzo.'),
                ('ACCETTAZIONE', 'I boss non stavano custodendo Neri. Erano parti della tua mente che costruivano prove, colpe e nuovi percorsi per non farti guardare la realta.'),
                ('VOCE', 'Neri se n e andata. Non puoi raggiungerla tornando indietro, e non puoi sapere ogni cosa che avrebbe potuto succedere. La ricerca finisce qui. Il ricordo non deve finire.')],
        }
        if stage_info:
            tag = 'battle_win_end'
            self.start_dialogue(stage_lines[stage_info['stage']], tag)
            return
        if kind == 'witness':
            # The four gatekeepers return only AFTER the special memory encounter.
            # They identify themselves in their own voices; the game never labels them during the search.
            reveal = [
                ('VOCE', 'Il frammento si dissolve. Per un istante pensi che la stanza sia vuota. Poi le quattro figure che hai sconfitto riappaiono ai margini della banchina.'),
                ('IL PORTIERE', 'Io ti dicevo che non eri degno e ti mandavo indietro. Se non arrivavi mai da Neri, non avresti dovuto scoprire che la strada era finita. Io ero la Negazione: la parte di te che non riusciva a credere che fosse davvero partita.'),
                ('IL GUARDIANO', 'Io urlavo di andartene, minacciavo di esplodere e ti respingevo. Era più facile essere furioso che sentire la mancanza. Io ero la Rabbia.'),
                ('IL MERCANTE', 'Io ti vendevo finali alternativi: la frase giusta, il saluto perfetto, il momento in cui avresti potuto cambiare tutto. Ma nessun patto poteva comprare un passato diverso. Io ero la Contrattazione.'),
                ('LA SENTINELLA', 'Io ti dicevo che non ti voleva vedere, che non meritavi di arrivare. Se ti convincevo a fermarti, non avresti rischiato di sperare ancora. Io ero la Depressione.'),
                ('ACCETTAZIONE', 'Non eravamo quattro nemici che tenevano Neri lontana da te. Eravamo quattro modi in cui la tua mente provava a proteggerti dal dolore, e intanto ti teneva fermo alla banchina.'),
                ('ACCETTAZIONE', 'Io non sono un quinto nemico da sconfiggere. Accettazione non significa che non ti manca, né che quello che è successo va bene. Significa smettere di chiedere al passato di cambiare.'),
                ('VOCE', 'Neri è partita. Non puoi raggiungerla tornando indietro. Ma puoi portare con te ciò che è stato senza trasformare ogni ricordo in una porta da riaprire.')
            ]
            self.start_dialogue(reveal, 'final_choice_pending')
            return
        endings = {
          'echo':[('IL NODO','...Il rumore non sparisce. Ma adesso so che non devo urlare per farmi ascoltare.'),('VOCE','La porta della citta suona. Per la prima volta, una campana non sembra un addio.')],
          'guilt':[('LA COLPA','Se smetti di accusarti, chi si ricordera di quanto ti importava?'),('VOCE','Tu. Il ricordo resta anche quando smetti di usarlo come punizione.')],
          'denial':[('IL RIFLESSO','E successo davvero. Non la raggiungerai. Avevo ragione, ma non era questo che volevo farti capire.'),('VOCE','Il riflesso si spezza. Non custodiva la strada per Neri: custodiva la porta che non volevi aprire. Dietro non c e una soluzione, solo il fatto che e partita e tu sei rimasto.')],
          'bargaining':[('LA CONTRATTAZIONE','Non esiste una frase capace di comprare un altro finale.'),('VOCE','Puoi riconoscere cosa avresti voluto fare senza fingere che avresti controllato tutto.')],
          'depression':[('LA DEPRESSIONE','Il vuoto non e un enigma da risolvere.'),('VOCE','Puoi smettere di chiedergli una risposta e camminare anche mentre ti accompagna.')],
          'perfection':[('LA PERFEZIONE','Non hai trovato la frase perfetta.'),('VOCE','Hai trovato una frase vera. Non e la stessa cosa, ma puo bastare.')],
          'grief':[('IL LUTTO','L’onda tornera.'),('VOCE','Si. Ma non ogni ritorno e una sconfitta.')],
          'anger':[('LA RABBIA','Sono ancora qui.'),('VOCE','Non devi cacciarla. Puoi ascoltarla senza consegnarle il volante.')],
          'fear':[('LA PAURA','Non posso prometterti che non farai piu male.'),('VOCE','Non te lo chiedono. Ti chiedono di non smettere di vivere solo per evitare il dolore.')],
          'shame':[('LA VERGOGNA','Mi hai visto.'),('VOCE','E non e successo niente di magico. Sei rimasto li, visibile, e il mondo non e finito.')],
          'doubt':[('IL DUBBIO','Continuero a fare domande.'),('VOCE','Certo. Ma non tutte le domande meritano di fermarti.')],
          'witness':[('ACCETTAZIONE','Non sono riuscito a fermarti. Forse non dovevo.'),('VOCE','Neri e partita. La ricerca finisce qui; il ricordo no.')],
          'control':[('IL DOVERE','Se non ti punisci, non significa che non ti importasse.'),('VOCE','La linea si spezza. Non devi pagare con la vita di oggi per dimostrare che il passato contava.')],
        }
        self.start_dialogue(endings.get(kind, [('VOCE','Il combattimento finisce, ma il ricordo resta.' )]), 'battle_win_end')

    def draw_battle(self, t):
        b = self.battle
        if not b:
            return
        stage_info = b.get('stage_info')
        if stage_info:
            actor, subtitle, color = stage_info['name'], stage_info['subtitle'], stage_info['color']
        else:
            actor, subtitle, color = BATTLE_NAMES.get(b['type'], ('L’AVVERSARIO', '(difesa interiore)', (124,208,224)))
        if b['type'] == 'witness' and stage_info is None:
            actor, subtitle, color = 'IL RICORDO', 'NON SCHIVARE: LASCIA CHE TI RAGGIUNGA', (129, 235, 210)
        phase_index = b['combat_phase']
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((3, 5, 18, 238))
        self.screen.blit(overlay, (0, 0))

        # Boss silhouette and halo: each emotional stage carries its own color and pulse.
        pulse = 4 + int(4 * (0.5 + 0.5 * math.sin(t * 3.2)))
        self.glow(WIDTH // 2, 70, color, 88 + pulse, 17 + pulse)
        emblem_x, emblem_y = WIDTH // 2, 70
        pygame.draw.circle(self.screen, color, (emblem_x, emblem_y), 21 + pulse, 2)
        pygame.draw.circle(self.screen, color, (emblem_x, emblem_y), 10 + pulse // 2, 1)
        if stage_info:
            stage_no = stage_info['stage']
            if stage_no == 1:  # Negazione: specchio incrinato
                pygame.draw.polygon(self.screen, (211, 239, 255), [(emblem_x, emblem_y-18), (emblem_x+7, emblem_y-3), (emblem_x-2, emblem_y+2)], 2)
                pygame.draw.polygon(self.screen, color, [(emblem_x+12, emblem_y-7), (emblem_x+4, emblem_y+4), (emblem_x+15, emblem_y+14)], 2)
                pygame.draw.line(self.screen, (211, 239, 255), (emblem_x-13, emblem_y+8), (emblem_x-2, emblem_y-1), 2)
            elif stage_no == 2:  # Rabbia: stella/spina
                spikes=[]
                for j in range(16):
                    a=-math.pi/2 + j*math.pi/8
                    r=18 if j%2==0 else 8
                    spikes.append((int(emblem_x+math.cos(a)*r), int(emblem_y+math.sin(a)*r)))
                pygame.draw.polygon(self.screen, color, spikes, 2)
                pygame.draw.circle(self.screen, (255, 229, 190), (emblem_x, emblem_y), 4)
            elif stage_no == 3:  # Contrattazione: due orbite che quasi si toccano
                pygame.draw.circle(self.screen, color, (emblem_x-8, emblem_y), 11, 2)
                pygame.draw.circle(self.screen, (255, 234, 192), (emblem_x+8, emblem_y), 11, 2)
                pygame.draw.line(self.screen, color, (emblem_x-2, emblem_y-5), (emblem_x+2, emblem_y+5), 2)
            elif stage_no == 4:  # Depressione: un nucleo sotto la linea dell'acqua
                pygame.draw.line(self.screen, color, (emblem_x-19, emblem_y-2), (emblem_x+19, emblem_y-2), 2)
                pygame.draw.circle(self.screen, (207, 219, 255), (emblem_x, emblem_y+8), 7, 2)
                pygame.draw.circle(self.screen, color, (emblem_x, emblem_y+8), 2)
            else:  # Accettazione: alba sul mare
                pygame.draw.arc(self.screen, (207, 255, 239), (emblem_x-15, emblem_y-15, 30, 30), math.pi, math.tau, 2)
                pygame.draw.line(self.screen, (207, 255, 239), (emblem_x-20, emblem_y+5), (emblem_x+20, emblem_y+5), 2)
                pygame.draw.arc(self.screen, color, (emblem_x-20, emblem_y+3, 40, 18), 0.1, math.pi-0.1, 2)
        draw_text(self.screen, self.medium_font, actor, color, (WIDTH // 2, 34), center=True)
        draw_text(self.screen, self.tiny_font, subtitle, (200, 214, 239), (WIDTH // 2, 105), center=True)

        # Enemy HP and stage phase are always visible.
        pygame.draw.rect(self.screen, (14, 19, 38), (275, 126, 410, 14), border_radius=5)
        ratio = b['boss_hp'] / max(1, b['max_boss_hp'])
        pygame.draw.rect(self.screen, color, (279, 130, int(402 * ratio), 6), border_radius=3)
        draw_text(self.screen, self.tiny_font, (f"RICORDO  {b['boss_hp']}/{b['max_boss_hp']}" if b.get('special_memory') else f"BOSS  {b['boss_hp']}/{b['max_boss_hp']} HP     FASE {min(3, phase_index + 1)}"), (209, 221, 242), (WIDTH // 2, 149), center=True)

        arena = pygame.Rect(258, 217, 444, 270)
        pygame.draw.rect(self.screen, (5, 9, 25), arena, border_radius=7)
        pygame.draw.rect(self.screen, color, arena, 2, border_radius=7)
        # Subtle arena grid adds readability without hiding projectile trajectories.
        for gx in range(arena.left + 28, arena.right - 10, 56):
            pygame.draw.line(self.screen, (17, 28, 49), (gx, arena.top + 8), (gx, arena.bottom - 8), 1)
        for gy in range(arena.top + 26, arena.bottom - 8, 42):
            pygame.draw.line(self.screen, (17, 28, 49), (arena.left + 8, gy), (arena.right - 8, gy), 1)

        if b['turn'] == 'player':
            draw_text(self.screen, self.small_font, 'IL TUO TURNO  ·  COLPISCI QUANDO IL SEGNALE È AL CENTRO', (150, 246, 200), (WIDTH // 2, 185), center=True)
            bar = pygame.Rect(300, 337, 360, 36)
            pygame.draw.rect(self.screen, (16, 25, 42), bar, border_radius=6)
            pygame.draw.rect(self.screen, (109, 139, 172), bar, 1, border_radius=6)
            pygame.draw.rect(self.screen, (67, 185, 148), (bar.centerx - 23, bar.y + 3, 46, bar.height - 6), border_radius=4)
            marker_x = int(b.get('marker_x', 320))
            pygame.draw.line(self.screen, (255, 231, 163), (marker_x, bar.y - 8), (marker_x, bar.bottom + 8), 4)
            pygame.draw.polygon(self.screen, (255, 244, 203), [(marker_x, bar.y - 13), (marker_x - 7, bar.y - 23), (marker_x + 7, bar.y - 23)])
            draw_text(self.screen, self.tiny_font, 'E / INVIO / SPAZIO', (187, 204, 227), (WIDTH // 2, 394), center=True)
            draw_text(self.screen, self.tiny_font, 'CENTRO = COLPO FORTE  ·  BORDI = COLPO DEBOLE', (154, 178, 204), (WIDTH // 2, 417), center=True)
        else:
            pattern_name = ('FRAMMENTO DI MEMORIA' if b.get('special_memory') else self._battle_pattern_name(b))
            warning = b['enemy_clock'] < 0.58
            state = ('NON SCHIVARE — LASCIA CHE TI RAGGIUNGA' if b.get('special_memory') else ('PREPARATI — ' + pattern_name if warning else 'ATTACCO NEMICO — SCHIVA!'))
            state_color = (255, 221, 145) if warning else (255, 112, 139)
            draw_text(self.screen, self.small_font, state, state_color, (WIDTH // 2, 185), center=True)
            if b.get('special_memory'):
                draw_text(self.screen, self.tiny_font, 'NON SCHIVARE — LASCIA CHE IL FRAMMENTO TI RAGGIUNGA', (195, 238, 225), (WIDTH // 2, 205), center=True)
            elif b['pattern'] % 5 == 0:
                ys = (258, 302, 346, 390, 434, 468)
                cue_n = b['spawn_count'] if warning else max(0, b['spawn_count'] - 1)
                gap = (b['rounds'] + (cue_n // 2) + b['rank']) % 6
                for i, sy in enumerate(ys):
                    col = (93, 235, 177) if i == gap and warning else ((255, 94, 133) if i != gap else (88, 202, 155))
                    pygame.draw.line(self.screen, col, (269, sy), (691, sy), 2 if warning else 1)
                if warning:
                    draw_text(self.screen, self.tiny_font, 'ONDA ORIZZONTALE — CERCA LA FASCIA LIBERA', (195, 212, 234), (WIDTH // 2, 205), center=True)
            elif b['pattern'] % 5 == 1:
                cue_n = b['spawn_count'] if warning else max(0, b['spawn_count'] - 1)
                sx = 315 + ((cue_n * 73 + b['rounds'] * 41) % 330)
                self.glow(sx, 243, (255, 107, 132), 37, 12)
                pygame.draw.circle(self.screen, (255, 129, 150), (int(sx), 243), 8, 2)
                draw_text(self.screen, self.tiny_font, 'MIRINO — IL COLPO TI SEGUE NELLA POSIZIONE DI LANCIO', (218, 194, 214), (WIDTH // 2, 205), center=True)
            elif b['pattern'] % 5 == 2:
                draw_text(self.screen, self.tiny_font, 'MURO — CERCA IL VARCO NELLA FILA DI PROIETTILI', (218, 194, 214), (WIDTH // 2, 205), center=True)
                cue_n = b['spawn_count'] if warning else max(0, b['spawn_count'] - 1)
                gap = (cue_n + b['rounds'] + b['rank']) % 6
                for i, gy in enumerate((254, 296, 338, 380, 422, 464)):
                    col = (95, 229, 174) if i == gap and warning else (240, 90, 125)
                    pygame.draw.line(self.screen, col, (269, gy), (690, gy), 2 if warning else 1)
            elif b['pattern'] % 5 == 3:
                draw_text(self.screen, self.tiny_font, 'SPIRALE — NON RESTARE VICINO AL CENTRO', (218, 194, 214), (WIDTH // 2, 205), center=True)
                pygame.draw.circle(self.screen, (255, 120, 158), (480, 358), 45 + int(8 * math.sin(t * 3)), 1)
            else:
                draw_text(self.screen, self.tiny_font, 'CROCE — LE TRAIETTORIE SI INCROCIANO', (218, 194, 214), (WIDTH // 2, 205), center=True)
                for xline in (322, 470, 618):
                    pygame.draw.line(self.screen, (119, 100, 147), (xline, 241), (xline + 35, 463), 1)

            # Signature threats have their own visible lane/aim cue, not surprise damage.
            stage_no = stage_info['stage'] if stage_info else 0
            cue_n = b['spawn_count'] if warning else max(0, b['spawn_count'] - 1)
            if stage_no == 2 and cue_n % 2 == 0 and b['pattern'] % 5 not in (2, 4):
                slash_y = 278 + ((cue_n * 43 + b['rounds'] * 19) % 160)
                pygame.draw.line(self.screen, (255, 110, 127), (269, slash_y), (691, slash_y), 2 if warning else 1)
                draw_text(self.screen, self.tiny_font, 'RABBIA: TAGLIO ORIZZONTALE', (255, 166, 174), (WIDTH // 2, 474), center=True)
            elif stage_no == 4 and cue_n % 2 == 1:
                drop_x = 355 + ((cue_n * 61) % 250)
                pygame.draw.line(self.screen, (164, 184, 255), (drop_x, 238), (drop_x, 476), 2 if warning else 1)
                draw_text(self.screen, self.tiny_font, 'DEPRESSIONE: ONDA LENTA', (182, 199, 255), (WIDTH // 2, 474), center=True)
            elif stage_no == 5 and phase_index >= 1:
                pygame.draw.line(self.screen, (157, 248, 221), (480, 358), (int(b['heart'][0]), int(b['heart'][1])), 2 if warning else 1)
                draw_text(self.screen, self.tiny_font, 'ACCETTAZIONE: ECO DIRETTA VERSO IL CUORE', (174, 246, 225), (WIDTH // 2, 474), center=True)

            # Every bullet is a moving object, not just a visual warning.
            for bullet in b['bullets']:
                bx, by, r = int(bullet['x']), int(bullet['y']), int(bullet['r'])
                ring, core, shine = ((85, 255, 218), (133, 255, 225), (232, 255, 248)) if bullet.get('memory') else ((255, 72, 111), (255, 146, 167), (255, 230, 235))
                pygame.draw.circle(self.screen, ring, (bx, by), r + 3, 1)
                pygame.draw.circle(self.screen, core, (bx, by), r)
                pygame.draw.circle(self.screen, shine, (bx, by), max(2, r // 3))

            hx, hy = b['heart']
            if b['hit_cd'] <= 0 or int(t * 18) % 2 == 0:
                self.glow(hx, hy, (255, 62, 111), 29, 47)
                heart = [(int(hx), int(hy - 10)), (int(hx + 10), int(hy)),
                         (int(hx), int(hy + 10)), (int(hx - 10), int(hy))]
                pygame.draw.polygon(self.screen, (255, 73, 121), heart)
                pygame.draw.polygon(self.screen, (255, 233, 239), heart, 1)

        # Two independent health bars; only the player's bar loses breath on collision.
        pygame.draw.rect(self.screen, (15, 21, 39), (276, 508, 408, 14), border_radius=5)
        hp_ratio = max(0, b['hp']) / max(1, b['max_player_hp'])
        pygame.draw.rect(self.screen, (255, 80, 126), (280, 512, int(400 * hp_ratio), 6), border_radius=3)
        draw_text(self.screen, self.tiny_font, f"TU  {max(0,b['hp'])}/{b['max_player_hp']} RESPIRO", (228, 216, 235), (280, 533))
        draw_text(self.screen, self.tiny_font, f"ROUND {b['rounds']}  ·  DIFFICOLTÀ {b['rank']}/10", (158, 181, 208), (680, 533), center=False)
        if b['damage_timer'] > 0:
            result = b['damage_text']
            result_color = (255, 228, 155) if 'PERFETTO' in result or 'CENTRATO' in result else (255, 151, 173)
            draw_text(self.screen, self.small_font, result, result_color, (WIDTH // 2, 565), center=True)
        elif b['turn_result_timer'] > 0:
            draw_text(self.screen, self.small_font, b['turn_result'], (255, 216, 145), (WIDTH // 2, 565), center=True)
        draw_text(self.screen, self.tiny_font, 'WASD / FRECCE: MUOVI  ·  SHIFT: SCATTO  ·  E: ATTACCA  ·  M: AUDIO',
                  (141, 163, 194), (WIDTH // 2, 610), center=True)

    def draw_story_map(self,t):
        data=self.scene; p=self.palette
        self.screen.blit(self.scene_surface,(0,0))
        self.glow(*self.npc_pos,p['glow'],90,22)
        for i,prop in enumerate(data['props']):
            pos=prop['pos']; done=i in self.state['props']; col=tuple(int(c*(0.45 if done else 1)) for c in p['glow'])
            pulse=math.sin(t*3+i)*3; self.glow(pos[0],pos[1],col,28,34 if not done else 8)
            if data['style'] in ('baggage','signal'):
                pygame.draw.rect(self.screen,(26,34,53),(pos[0]-13,pos[1]-12,26,24),border_radius=3)
                pygame.draw.rect(self.screen,col,(pos[0]-13,pos[1]-12,26,24),2,border_radius=3)
                if prop.get('key_item'): pygame.draw.circle(self.screen,(255,219,133),(int(pos[0]),int(pos[1])),4)
            elif data['style'] in ('library','paper','archive','press'):
                pygame.draw.rect(self.screen,(41,29,52),(pos[0]-10,pos[1]-14,20,28)); pygame.draw.rect(self.screen,col,(pos[0]-10,pos[1]-14,20,28),1)
            elif data['style'] in ('house','bedroom','attic'):
                pygame.draw.rect(self.screen,(45,49,64),(pos[0]-12,pos[1]-15,24,30),border_radius=2); pygame.draw.rect(self.screen,col,(pos[0]-12,pos[1]-15,24,30),1,border_radius=2)
            else:
                pygame.draw.polygon(self.screen,col,[(pos[0],pos[1]-13-pulse),(pos[0]+11,pos[1]),(pos[0],pos[1]+13+pulse),(pos[0]-11,pos[1])])
            if i not in self.state['props']:
                label=prop['name']; w=min(220,self.tiny_font.size(label)[0]+10)
                pygame.draw.rect(self.screen,(5,9,23),(int(pos[0]-w/2),int(pos[1]+18),w,17),border_radius=2)
                draw_text(self.screen,self.tiny_font,label,(219,228,242),(pos[0],pos[1]+26),center=True,shadow=False)
        npc_color=BATTLE_NAMES[data['battle']][2] if data['battle'] in BATTLE_NAMES else (255,206,145) if data['chapter'] in (1,5,6) else p['glow']
        self.draw_extra_character(*self.npc_pos,t,data['npc'],npc_color)
        # Rune and route markers are shown only while the player has activated the task.
        if data['task'] in ('runes','route','tidal') and self.state['started'] and not self.state['clear']:
            for i,pos in enumerate(data['route']):
                done=i<self.state['progress']; col=(114,232,211) if done else ((255,218,128) if i==self.state['progress'] else p['line'])
                self.glow(*pos,col,35,38 if i==self.state['progress'] else 16)
                pygame.draw.circle(self.screen,col,(int(pos[0]),int(pos[1])),11 if not done else 7,2)
                draw_text(self.screen,self.tiny_font,str(i+1),(245,247,250),pos,center=True,shadow=False)
        if data['task']=='stealth' and self.state['started'] and not self.state['clear']:
            beamx=480+math.sin(t*0.88)*335; beamy=315+math.sin(t*1.17)*58; active=(self.story_t%2.8)>2.02
            beam_col=(255,112,150) if active else (102,151,188)
            pygame.draw.line(self.screen,beam_col,(beamx,220),(beamx,410),5 if active else 2)
            self.glow(beamx,beamy,beam_col,50,28 if active else 8)
            for pos in data['route']:
                pygame.draw.ellipse(self.screen,(19,39,55),(pos[0]-22,pos[1]-13,44,26)); pygame.draw.ellipse(self.screen,(83,166,173),(pos[0]-22,pos[1]-13,44,26),1)
        if data['task']=='tidal' and self.state['started'] and not self.state['clear']:
            phase=self.story_t%3.6; low=phase<2.25
            wave_col=(70,190,206) if low else (39,113,151)
            for yy in (245,360,445): pygame.draw.line(self.screen,wave_col,(0,yy+int(math.sin(t*2+yy)*5)),(WIDTH,yy+int(math.sin(t*2+yy)*5)),2)
        if data['task']=='memory_walk' and self.state['started'] and not self.state['clear']:
            for i,pos in enumerate(data['route']):
                active=i==self.state['progress']; col=(255,221,145) if active else (94,130,164)
                self.glow(*pos,col,30,28 if active else 9); pygame.draw.circle(self.screen,col,(int(pos[0]),int(pos[1])),9 if active else 5,1)
        if data['task']=='rhythm' and self.rhythm_active:
            phase=self.rhythm_clock%1.8; active=0.58<=phase<=1.08
            pygame.draw.rect(self.screen,(5,8,24),(WIDTH//2-150,HEIGHT-128,300,18),border_radius=4)
            pygame.draw.rect(self.screen,(255,219,132) if active else (80,91,126),(WIDTH//2-150,HEIGHT-128,300,18),2,border_radius=4)
            pulse_x=WIDTH//2-150+int(300*phase/1.8)
            pygame.draw.circle(self.screen,(255,233,155) if active else (152,166,204),(pulse_x,HEIGHT-119),8)
            draw_text(self.screen,self.small_font,f'RESPIRI {self.rhythm_hits}/3 — E SUL LAMPO',(229,233,246),(WIDTH//2,HEIGHT-145),center=True)
        for particle in self.particles: particle.draw(self.screen)
        self.draw_player()
        self.screen.blit(self.vignette,(0,0))
        self.draw_story_hud()
        self.draw_dialogue()
        if self.choice_pending and not self.dialogue:
            self.draw_choice_panel()
        if self.hint_timer>0 and not self.dialogue:
            ww=min(WIDTH-40,self.small_font.size(self.hint_text)[0]+28)
            pygame.draw.rect(self.screen,(5,9,24),(WIDTH//2-ww//2,72,ww,32),border_radius=4)
            pygame.draw.rect(self.screen,p['glow'],(WIDTH//2-ww//2,72,3,32))
            draw_text(self.screen,self.small_font,self.hint_text,(232,239,247),(WIDTH//2,80))
        if self.room_title_timer>0:
            alpha=min(1.0,self.room_title_timer*1.5)
            card_title=self.medium_font.render(CHAPTER_TITLES.get(data['chapter'], 'LUCE SOMMERSA'),False,(255,220,143))
            card_title.set_alpha(int(alpha*235)); rr=card_title.get_rect(center=(WIDTH//2,83)); self.screen.blit(card_title,rr)
            subtitle=self.small_font.render(data['title'],False,(232,246,250)); subtitle.set_alpha(int(alpha*225))
            self.screen.blit(subtitle,subtitle.get_rect(center=(WIDTH//2,108)))
            pygame.draw.line(self.screen,p['glow'],(WIDTH//2-170,129),(WIDTH//2+170,129),1)
        if self.flash_timer>0:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((*p['glow'],int(45*min(1,self.flash_timer/.22)))); self.screen.blit(ov,(0,0))
        if self.battle_active: self.draw_battle(t)
        pygame.display.flip()

    def draw_choice_panel(self):
        data=self.scene; opts=data.get('second_options',data['options']) if data['task']=='conversation' and self.state.get('conversation_stage',1)>=2 else data['options']
        panel=pygame.Surface((700,180),pygame.SRCALPHA); panel.fill((4,8,22,242))
        pygame.draw.rect(panel,self.palette['glow'],(0,0,4,180))
        self.screen.blit(panel,(130,390))
        prompt='CHE COSA SCEGLI DI PORTARE CON TE?' if self.scene_id=='witness' else (data.get('second_prompt','SCEGLI COME CONTINUARE') if data['task']=='conversation' and self.state.get('conversation_stage',1)>=2 else ('CHE COSA VUOI DIRE?' if data['task']=='conversation' else 'SCEGLI UNA RISPOSTA  ·  1 / 2 / 3'))
        draw_text(self.screen,self.small_font,prompt,(255,220,140),(WIDTH//2,405),center=True)
        for i,(label,explain) in enumerate(opts):
            draw_text(self.screen,self.small_font,f'{i+1}  {label}',(235,237,246),(165,438+i*38))
            draw_text(self.screen,self.tiny_font,explain,(151,173,203),(365,441+i*38))

    def draw_story_hud(self):
        data=self.scene; p=self.palette; st=self.state
        pygame.draw.rect(self.screen,(5,9,22),(17,16,420,49),border_radius=4); pygame.draw.rect(self.screen,p['glow'],(17,16,3,49))
        chapter_scenes = SCENES_BY_CHAPTER.get(data['chapter'], [self.scene_id])
        room_no = chapter_scenes.index(self.scene_id) + 1 if self.scene_id in chapter_scenes else 1
        room_count = len(chapter_scenes)
        route_label = 'DEVIAZIONE FACOLTATIVA' if data.get('is_side_room') else f'AREA {room_no}/{room_count}'
        draw_text(self.screen,self.tiny_font,f'LUCE SOMMERSA  /  CAPITOLO {data["chapter"]:02d}  ·  {route_label}',(151,217,229),(30,22))
        draw_text(self.screen,self.small_font,data['title'],(232,236,246),(30,38))
        if self.inventory:
            items=[]
            if 'numero_cabina' in self.inventory: items.append('INDIZIO S-17')
            if 'chiave_carrozza' in self.inventory: items.append('CHIAVE DELLA TORRE')
            if items: draw_text(self.screen,self.tiny_font,'INVENTARIO  ·  '+'  /  '.join(items),(255,220,143),(30,72))
        task_hint={ 'two_step':'Parla con Pip e poi leggi il tabellone.','runes':'Attraversa le luci in sequenza.','sequence':'Ricomponi la sequenza.','choice':'Parla e scegli 1, 2 o 3.','rhythm':'Segui il battito della luce.','route':'Segui il percorso che appare.','battle':'Ascolta il tuo avversario interiore.','final_battle':'Il Testimone cambia regola.','memory':'Fermati vicino alla sedia.','chase':'Segui il Capocorsa. Poi esplora le carrozze: la torre richiede una chiave.','stealth':'Nasconditi dalle voci che scansionano il tunnel.','conversation':'La conversazione ha due passaggi: scegli con calma.','memory_walk':'Attraversa i punti del ricordo.','tidal':'Muoviti quando la marea si ritira.','battle':'Ascolta il tuo avversario interiore.'}.get(data['task'],'Esplora e interagisci.')
        if st['clear']:
            if self.scene_id == 'tram' and 'chiave_carrozza' not in self.inventory:
                task_hint='OBIETTIVO: esplora le due carrozze laterali e recupera la chiave della torre.'
            else:
                task_hint='Passaggio aperto: raggiungi la soglia luminosa.'
        hint_w=self.tiny_font.size(task_hint)[0]
        draw_text(self.screen,self.tiny_font,task_hint,(183,198,219),(WIDTH-hint_w-18,23),center=False)
        if not self.dialogue:
            text='WASD/FRECCE muovi  ·  SHIFT scatto  ·  E interagisci  ·  M audio'
            draw_text(self.screen,self.tiny_font,text,(137,154,180),(WIDTH//2,HEIGHT-18),center=True)
        if not st['clear'] and data['exit']:
            draw_text(self.screen,self.tiny_font,'SOGLIA CHIUSA',(198,175,199),(WIDTH//2,HEIGHT-43),center=True)

    def draw_ending(self,t):
        self.screen.fill((5,8,23))
        for i in range(70):
            x=(i*137+int(t*9))%WIDTH; y=(i*79+int(math.sin(t+i)*11))%HEIGHT
            self.glow(x,y,(94,178,201),20,8)
        title='LA LUCE NON CANCELLA IL MARE'
        draw_text(self.screen,self.big_font,title,(222,246,239),(WIDTH//2,120),center=True)
        lines=self.story_ending or ['Neri e andata avanti. Tu puoi fare lo stesso, senza cancellare quello che provavi.']
        if isinstance(lines, str): lines = [lines]
        for i,line in enumerate(lines): draw_text(self.screen,self.font,line,(184,207,226),(WIDTH//2,220+i*38),center=True)
        if 'lobby' in self.story_choices:
            mask=['Hai imparato a chiedere aiuto.','Hai dato una voce alla rabbia.','Per ora, la maschera resta con te.'][self.story_choices['lobby']-1]
            draw_text(self.screen,self.small_font,mask,(165,219,220),(WIDTH//2,420),center=True)
        if 'market' in self.story_choices:
            choice=['Hai scelto la verita.','Hai scelto il rimorso.','Hai scelto la fuga.'][self.story_choices['market']-1]
            draw_text(self.screen,self.small_font,choice,(165,219,220),(WIDTH//2,448),center=True)
        if 'dining_first' in self.story_choices:
            memory_choice=['Hai dato spazio alla rabbia.','Hai nominato la paura.','Hai accettato un vuoto nella memoria.'][self.story_choices['dining_first']-1]
            draw_text(self.screen,self.small_font,memory_choice,(165,219,220),(WIDTH//2,476),center=True)
        if 'dining' in self.story_choices:
            final_choice=['Hai chiesto scusa senza pretendere assoluzione.','Hai detto che ti mancava senza chiederle di tornare.','Hai riconosciuto il desiderio senza farne una pretesa.'][self.story_choices['dining']-1]
            draw_text(self.screen,self.tiny_font,final_choice,(165,219,220),(WIDTH//2,504),center=True)
        draw_text(self.screen,self.small_font,'INVIO: RICOMINCIA     ESC: ESCI',(139,158,184),(WIDTH//2,530),center=True)
        pygame.display.flip()

    def draw(self,t):
        if not self.started:
            self.screen.fill((5,10,26))
            for i in range(55):
                x=(i*97+int(t*4))%WIDTH; y=(i*61+int(math.sin(t+i)*9))%HEIGHT
                self.glow(x,y,(72,209,221),24,10)
            draw_text(self.screen,self.big_font,'LUCE SOMMERSA',(225,247,245),(WIDTH//2,170),center=True)
            draw_text(self.screen,self.medium_font,'NON TUTTO CIO CHE CERCHI E RIMASTO INDIETRO',(186,208,235),(WIDTH//2,225),center=True)
            intro=['31 ambienti in 10 capitoli narrativi.','Esplorazione, enigmi, scelte e una caccia a Neri.','Quattro boss a turni, più un incontro finale con una regola diversa.','Quattro boss principali e un incontro finale speciale.']
            for i,line in enumerate(intro): draw_text(self.screen,self.font,line,(159,183,212),(WIDTH//2,315+i*31),center=True)
            draw_text(self.screen,self.medium_font,'PREMI INVIO PER INIZIARE',(255,219,139),(WIDTH//2,490),center=True)
            draw_text(self.screen,self.small_font,'WASD / FRECCE  ·  E INTERAGISCI  ·  SHIFT SCATTO  ·  M AUDIO',(131,153,183),(WIDTH//2,545),center=True)
            pygame.display.flip(); return
        if self.ending:
            self.draw_ending(t); return
        self.draw_story_map(t)

    def run(self):
        while True:
            dt=min(self.clock.tick(60)/1000.0,0.04)
            for event in pygame.event.get(): self.handle_event(event)
            keys=pygame.key.get_pressed(); self.update(dt,keys); self.draw(pygame.time.get_ticks()/1000.0)


def main():
    try: StoryGame().run()
    except KeyboardInterrupt: pygame.quit()

if __name__=='__main__': main()
