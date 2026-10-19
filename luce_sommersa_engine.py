#!/usr/bin/env python3
# LUCE SOMMERSA — una piccola avventura esplorativa in pixel art.
# Requisito: pygame (su Ubuntu: sudo apt install python3-pygame)

import math
import random
import sys
import hashlib
from pathlib import Path
import pygame

WIDTH, HEIGHT = 960, 640
TILE = 32
FPS = 60
TITLE = "LUCE SOMMERSA"

# Palette per stanza: il colore della luce cambia con la storia.
PALETTES = {
    0: {"floor": (16, 25, 42), "floor2": (19, 31, 50), "wall": (31, 45, 64), "line": (42, 67, 85), "glow": (77, 218, 224), "dust": (102, 217, 220)},
    1: {"floor": (17, 27, 47), "floor2": (21, 38, 59), "wall": (35, 48, 78), "line": (70, 87, 126), "glow": (123, 117, 255), "dust": (177, 164, 255)},
    2: {"floor": (18, 16, 34), "floor2": (28, 18, 42), "wall": (43, 28, 56), "line": (80, 39, 81), "glow": (255, 89, 165), "dust": (255, 112, 173)},
}


def clamp(value, low, high):
    return max(low, min(high, value))


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def draw_text(surface, font, text, color, pos, center=False, shadow=True):
    if shadow:
        shadow_image = font.render(text, False, (4, 7, 15))
        rect = shadow_image.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        surface.blit(shadow_image, (rect.x + 2, rect.y + 3))
    image = font.render(text, False, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)
    return rect


# Palette originali per i capitoli 2-10. Ogni luogo cambia anche il tono della luce.
EXTRA_PALETTES = {
    3:  {"floor": (22, 28, 48), "floor2": (28, 34, 59), "wall": (42, 52, 83), "line": (59, 80, 117), "glow": (255, 205, 112), "dust": (255, 222, 145)},
    4:  {"floor": (30, 20, 43), "floor2": (39, 24, 55), "wall": (59, 35, 75), "line": (96, 53, 107), "glow": (246, 124, 196), "dust": (255, 165, 215)},
    5:  {"floor": (18, 24, 43), "floor2": (22, 31, 54), "wall": (35, 46, 72), "line": (54, 76, 107), "glow": (167, 166, 255), "dust": (193, 190, 255)},
    6:  {"floor": (22, 28, 42), "floor2": (28, 36, 51), "wall": (46, 53, 66), "line": (75, 91, 105), "glow": (255, 203, 132), "dust": (255, 220, 163)},
    7:  {"floor": (28, 18, 38), "floor2": (36, 21, 49), "wall": (53, 30, 67), "line": (92, 43, 98), "glow": (255, 113, 164), "dust": (255, 160, 198)},
    8:  {"floor": (12, 31, 42), "floor2": (17, 39, 50), "wall": (27, 53, 66), "line": (40, 84, 94), "glow": (103, 236, 217), "dust": (150, 255, 228)},
    9:  {"floor": (20, 24, 39), "floor2": (29, 28, 48), "wall": (43, 43, 65), "line": (74, 75, 112), "glow": (185, 145, 255), "dust": (206, 180, 255)},
    10: {"floor": (27, 21, 37), "floor2": (36, 26, 47), "wall": (52, 34, 65), "line": (93, 54, 100), "glow": (255, 171, 194), "dust": (255, 204, 212)},
    11: {"floor": (8, 14, 29), "floor2": (14, 20, 39), "wall": (27, 31, 53), "line": (56, 62, 97), "glow": (131, 246, 229), "dust": (183, 255, 239)},
}
PALETTES.update(EXTRA_PALETTES)

# Ogni capitolo ha una piccola missione ambientale: niente grind o statistiche.
# Le missioni si risolvono muovendosi e, in alcuni luoghi, interagendo con E.
CHAPTERS = {
    2: {
        "title": "LA CITTA DEI CAMPANELLI", "npc": "DADO", "npc_pos": (490, 315), "mode": "sequence", "order": [2, 1, 0],
        "goal": "Segui i tre campanelli: est, centro, ovest.",
        "intro": [("VOCE", "La citta suona, ma nessuna campana ha una lingua."), ("VOCE", "Le finestre si accendono quando passi. Dietro i vetri non c'e nessuno."), ("VOCE", "Cerchi qualcuno da liberare. La frase e tua, ma non ricordi chi te l'abbia affidata.")],
        "npc_lines": [("DADO", "Sono il custode dei suoni che nessuno ha avuto il coraggio di emettere."), ("DADO", "Tre rintocchi. Non seguirli con le orecchie: seguili con i piedi. Prima quello lontano, poi quello sotto la luna, infine quello vicino al ponte.")],
        "items": [
            {"name": "Campana del ponte", "pos": (215, 205), "line": ("CAMPANA", "Il primo rintocco non dice un nome. Dice: aspetta.")},
            {"name": "Campana di luna", "pos": (480, 145), "line": ("CAMPANA", "Il secondo rintocco ha due battiti, come se qualcuno camminasse accanto a te.")},
            {"name": "Campana lontana", "pos": (760, 405), "line": ("CAMPANA", "Il terzo rintocco sa di una partenza. Una mano si allontana dal vetro di un treno.")},
        ],
        "complete": [("VOCE", "Per un secondo senti un'altra persona camminare al tuo fianco. Quando ti volti, resta soltanto il suono."), ("DADO", "La strada per il mercato e aperta. Non comprare la prima risposta che ti offre.")],
    },
    3: {
        "title": "IL MERCATO DELLE COSE PERDUTE", "npc": "LUMA", "npc_pos": (485, 315), "mode": "collect", "order": [0, 1, 2],
        "goal": "Raccogli i tre oggetti che sembrano tuoi.",
        "intro": [("VOCE", "Al mercato si vendono cose che nessuno ha davvero perso."), ("VOCE", "Un mercante vende bottoni spaiati, fotografie senza volti e promesse avvolte nella carta."), ("VOCE", "Tre oggetti ti riconoscono. Tu non riconosci loro.")],
        "npc_lines": [("LUMA", "Qui non si paga con monete. Si paga con la certezza di ricordare bene."), ("LUMA", "Non comprare niente. Le cose che ti cercano si avvicineranno da sole.")],
        "items": [
            {"name": "Cartolina blu", "pos": (230, 410), "line": ("CARTOLINA", "Sul retro: 'Il posto accanto a me e tuo, anche quando non ci sei.'")},
            {"name": "Tazza scheggiata", "pos": (700, 180), "line": ("TAZZA", "Due impronte sul bordo. Una e la tua. L'altra finisce a meta, come se la memoria avesse trattenuto il fiato.")},
            {"name": "Biglietto piegato", "pos": (730, 450), "line": ("BIGLIETTO", "Destinazione: altrove. Passeggero: illeggibile. Sul bordo hai scritto: 'non dimenticare'.")},
        ],
        "complete": [("LUMA", "Non hai comprato niente. Hai riconosciuto qualcosa, che e piu difficile."), ("VOCE", "Nel riflesso di una vetrina compare una ragazza con una sciarpa rossa. Non riesci a ricordare il suo viso, ma ricordi come rideva.")],
    },
    4: {
        "title": "LA BIBLIOTECA DELLE FRASI NON DETTE", "npc": "SIBIL", "npc_pos": (480, 315), "mode": "sequence", "order": [2, 0, 1],
        "goal": "Cammina sulle frasi nell'ordine: fine, inizio, risposta.",
        "intro": [("VOCE", "In questa biblioteca, le frasi non dette hanno scaffali piu alti delle persone."), ("VOCE", "I libri si aprono quando smetti di cercare la frase perfetta."), ("VOCE", "Qualcuno ha lasciato tre righe sul pavimento. Sembrano fuori ordine, come un ricordo raccontato troppe volte.")],
        "npc_lines": [("SIBIL", "Le parole sono strane: alcune fanno male solo finche restano chiuse."), ("SIBIL", "Il ricordo piu vecchio sta alla fine del corridoio. Poi viene l'inizio. La risposta e quella al centro. Leggi camminando.")],
        "items": [
            {"name": "Frase: volevo restare", "pos": (235, 235), "line": ("PAGINA", "'Volevo restare.' La frase finisce prima di spiegare perche sei andato via.")},
            {"name": "Frase: non e colpa tua", "pos": (485, 430), "line": ("PAGINA", "'Non e colpa tua.' Non sai chi l'abbia detto, ma senti che qualcuno aveva bisogno di sentirlo.")},
            {"name": "Frase: aspetta", "pos": (740, 210), "line": ("PAGINA", "'Aspetta.' Una parola cosi piccola da non riuscire a fermare un treno.")},
        ],
        "complete": [("SIBIL", "Ora le frasi hanno un ordine. Non significa che siano facili da pronunciare."), ("VOCE", "Per la prima volta senti un nome dietro i pensieri: Neri. Il ricordo si ritira prima di mostrarti il volto.")],
    },
    5: {
        "title": "L'OSPEDALE DEI GIORNI SOSPESI", "npc": "ADA", "npc_pos": (490, 315), "mode": "sequence", "order": [0, 1, 2],
        "goal": "Segui le luci della sala d'attesa, dalla piu fioca alla piu calda.",
        "intro": [("VOCE", "Qui il tempo non cura niente: aspetta soltanto che tu torni."), ("VOCE", "Non ci sono pazienti, soltanto sedie rivolte verso porte che non si aprono."), ("VOCE", "Sotto ogni sedia pulsa una luce: il prima, l'attesa, il dopo.")],
        "npc_lines": [("ADA", "Non e un ospedale per i corpi. Qui vengono le attese che non hanno trovato una fine."), ("ADA", "La luce piu debole viene prima. Poi quella del corridoio. Infine quella sotto la finestra. Non puoi saltare l'attesa.")],
        "items": [
            {"name": "Luce del prima", "pos": (220, 420), "line": ("RICORDO", "Il prima: sei arrivato presto alla stazione. Avevi preparato una frase per non dover improvvisare.")},
            {"name": "Luce dell'attesa", "pos": (480, 270), "line": ("RICORDO", "L'attesa: hai riletto il biglietto fino a consumarne una piega. Non volevi che il treno partisse, ma non sapevi come chiederglielo.")},
            {"name": "Luce del dopo", "pos": (755, 420), "line": ("RICORDO", "Il dopo: il treno se n'e andato. Tu sei rimasto fermo, convinto che non piangere significasse essere forte.")},
        ],
        "complete": [("ADA", "Aspettare non cambia cio che e successo. Ma smette di essere l'unica cosa che sai fare."), ("VOCE", "La ragazza con la sciarpa rossa adesso ha un nome intero nel tuo ricordo: Neri. Era reale. E ti manca ancora.")],
    },
    6: {
        "title": "IL TEATRO DELLE MASCHERE", "npc": "CAPOCOMICO", "npc_pos": (480, 150), "mode": "interact", "order": [0, 1, 2],
        "goal": "Avvicinati alle tre maschere e premi E per ascoltarle.",
        "intro": [("VOCE", "Il teatro e pieno, eppure nessuno e venuto a vedere te."), ("VOCE", "Tre maschere stanno al centro del palco. Non attaccano. Aspettano che tu scelga quale guardare.")],
        "npc_lines": [("CAPOCOMICO", "Non c'e un premio per la maschera piu convincente."), ("CAPOCOMICO", "Avvicinati. Nessuna di loro e un nemico da sconfiggere. Sono tre modi diversi in cui hai imparato a proteggerti.")],
        "items": [
            {"name": "Maschera della colpa", "pos": (230, 350), "line": ("COLPA", "Se avessi trovato le parole giuste, forse sarebbe rimasta. La maschera si incrina: non puoi sapere come sarebbe andata.")},
            {"name": "Maschera della rabbia", "pos": (480, 375), "line": ("RABBIA", "Perche e partita senza capire quanto ti importasse? La maschera abbassa gli occhi. Anche lei non aveva modo di leggere i tuoi pensieri.")},
            {"name": "Maschera del silenzio", "pos": (730, 350), "line": ("SILENZIO", "Hai fatto finta di non aver bisogno di nessuno. Questa maschera non si rompe: si posa a terra, come un costume alla fine dello spettacolo.")},
        ],
        "complete": [("CAPOCOMICO", "La scena e finita. Non devi scegliere una sola emozione e chiamarla verita."), ("VOCE", "Dietro il sipario c'e una porta, e sulla porta e inciso un profilo che assomiglia al tuo.")],
    },
    7: {
        "title": "IL LAGO CAPOVOLTO", "npc": "RIFLESSO", "npc_pos": (480, 315), "mode": "collect", "order": [0, 1, 2],
        "goal": "Raggiungi i tre riflessi che non seguono i tuoi movimenti.",
        "intro": [("VOCE", "Il lago riflette cose che non sono mai successe, e cose che hai dimenticato."), ("VOCE", "Sull'acqua cammina la tua ombra. Ma ogni tanto si ferma e guarda indietro."), ("VOCE", "Tre riflessi brillano dove non dovrebbe esserci terra.")],
        "npc_lines": [("RIFLESSO", "Io non sono il futuro che avresti avuto. Sono le domande che non hai mai fatto."), ("RIFLESSO", "Non cercare la versione giusta di te. Cerca quella che hai lasciato ferma sulla banchina.")],
        "items": [
            {"name": "Riflesso del volto", "pos": (230, 200), "line": ("ACQUA", "Il tuo volto e nitido. Dietro la spalla, una seconda ombra tiene in mano un biglietto.")},
            {"name": "Riflesso del posto vuoto", "pos": (490, 440), "line": ("ACQUA", "Il posto accanto a te non e vuoto perche nessuno l'abbia mai occupato. E vuoto perche continui a voltarti verso di esso.")},
            {"name": "Riflesso della sciarpa", "pos": (755, 200), "line": ("ACQUA", "La sciarpa rossa gira nel vento. Ora ricordi la risata di Neri, ma non ancora le parole del vostro ultimo incontro.")},
        ],
        "complete": [("RIFLESSO", "La memoria non e una finestra. E acqua: trattiene la luce, ma non la forma."), ("VOCE", "Sotto il lago appare il tetto di una casa. Sai che e la tua, anche se non ricordi quando ci sei stato l'ultima volta.")],
    },
    8: {
        "title": "LA CASA SENZA PORTE", "npc": "NONNA ORA", "npc_pos": (490, 155), "mode": "interact", "order": [0, 1, 2],
        "goal": "Esamina la cornice, la sedia e il biglietto con E.",
        "intro": [("VOCE", "La casa ha tutte le stanze che ricordi, tranne quella in cui hai detto addio."), ("VOCE", "La cucina odora di pioggia e pane tostato. Nessuna porta conduce fuori: ogni stanza si apre quando smetti di evitarla.")],
        "npc_lines": [("NONNA ORA", "Le case ricordano le persone in modo diverso dalle fotografie."), ("NONNA ORA", "Non ti chiedero di perdonarti. Prima guarda cosa e successo, senza aggiungere una punizione alla storia.")],
        "items": [
            {"name": "Cornice vuota", "pos": (230, 320), "line": ("CORNICE", "La fotografia non e sparita. Sei stato tu a girarla verso il muro, il giorno dopo la partenza di Neri.")},
            {"name": "Sedia accanto alla finestra", "pos": (480, 420), "line": ("SEDIA", "Vi sedevate qui a inventare nomi per le nuvole. L'ultimo giorno hai lasciato la sedia vuota, per non dover dire che ti dispiaceva.")},
            {"name": "Biglietto mai consegnato", "pos": (740, 320), "line": ("LETTERA", "'Volevo chiederti di restare, ma non sarebbe stato giusto. Avevo paura che, se ti salutavo, ti avrei perso per sempre.'")},
        ],
        "complete": [("NONNA ORA", "Un addio non e una promessa tradita. E una cosa che a volte arriva prima che tu sia pronto."), ("VOCE", "Ora sai cosa vuoi liberare. Ma non e Neri, non davvero: lei ha continuato la sua vita. Tu sei rimasto in quella stazione.")],
    },
    9: {
        "title": "L'ARCHIVIO DEL PRIMO GIORNO", "npc": "ARCHIVISTA", "npc_pos": (485, 315), "mode": "sequence", "order": [2, 1, 0],
        "goal": "Ascolta i registri dal piu recente al piu antico: 03, 02, 01.",
        "intro": [("VOCE", "L'archivio conserva ogni versione della verita, persino quelle che hai cambiato."), ("VOCE", "Non troverai un ricordo perfetto. Troverai i tagli, le correzioni e le frasi che hai aggiunto per rendere sopportabile il silenzio.")],
        "npc_lines": [("ARCHIVISTA", "Il registro piu recente e in fondo. Parti dal numero 03, poi 02, poi 01."), ("ARCHIVISTA", "La verita non sempre assolve. Ma almeno smette di obbligarti a indovinare.")],
        "items": [
            {"name": "Registro 01", "pos": (225, 215), "line": ("REGISTRO 01", "Neri ti disse che sarebbe partita. Tu rispondesti 'va bene' senza guardarla. Non era indifferenza: era paura di farle vedere quanto contasse.")},
            {"name": "Registro 02", "pos": (485, 425), "line": ("REGISTRO 02", "Al binario avevi il biglietto in tasca e una frase pronta. Quando la vedesti arrivare, la frase scomparve. Lei non poteva sapere cosa avevi deciso di non dire.")},
            {"name": "Registro 03", "pos": (750, 215), "line": ("REGISTRO 03", "Il treno parti. Neri ti saluto dal finestrino. Tu non alzasti la mano fino a quando il vagone era gia lontano. Questo e il momento che hai continuato a ripetere.")},
        ],
        "complete": [("ARCHIVISTA", "Non sei responsabile di tutto cio che e successo. Sei responsabile solo di cosa farai con cio che ricordi adesso."), ("VOCE", "La persona che cerchi non e rimasta intrappolata da Neri. Sei stato tu a lasciare qui una parte di te, per non sentire quanto ti mancasse.")],
    },
    10: {
        "title": "LA STANZA CHE TI ASPETTA", "npc": "IL TESTIMONE", "npc_pos": (490, 285), "mode": "collect", "order": [0, 1, 2],
        "goal": "Raccogli gli ultimi tre frammenti, poi parla con la figura al centro.",
        "intro": [("VOCE", "La porta finale non e chiusa a chiave. Sei tu che non sei ancora entrato."), ("VOCE", "La stanza e semplice: una banchina, due ombre e una luce d'alba che non appartiene a nessun cielo.")],
        "npc_lines": [("IL TESTIMONE", "Ti ho aspettato finche hai smesso di chiamarmi Neri."), ("IL TESTIMONE", "Io non sono lei. Sono la parte di te che e rimasta sulla banchina, convinta che sentire la mancanza fosse una colpa."), ("IL TESTIMONE", "Non devi lasciarmi qui per andare avanti. Devi smettere di chiedermi di custodire da solo quel giorno.")],
        "items": [
            {"name": "Il biglietto", "pos": (225, 420), "line": ("FRAMMENTO", "Il biglietto non e una prova che avresti potuto fermare il treno. E la prova che eri li, e che ti importava.")},
            {"name": "La mano alzata", "pos": (490, 150), "line": ("FRAMMENTO", "Finalmente ricordi la tua mano alzarsi. Troppo tardi per cambiare il saluto, abbastanza presto per smettere di cancellarlo.")},
            {"name": "Il posto accanto", "pos": (755, 420), "line": ("FRAMMENTO", "Il posto accanto non deve restare occupato per sempre. Ma non deve neanche essere dimenticato per fare spazio al futuro.")},
        ],
        "complete": [("VOCE", "I frammenti si allineano. La figura al centro ha il tuo stesso passo, ma non abbassa piu lo sguardo.")],
    },
}


# Mappe artigianali dei capitoli 2-10. Ogni mappa e composta da ambienti
# collegati in modo diverso: non e una stanza standard a cui cambia il colore.
# Le coordinate sono nel mondo 960x640. I blocchi sono mobili/architetture solide.
EXTRA_LAYOUTS = {
    2: {"style": "bells", "floor": [
        (0, 278, 355, 84), (95, 128, 215, 190), (285, 205, 340, 220),
        (375, 74, 200, 174), (555, 278, 405, 84), (650, 330, 245, 190)],
        "blocks": [(112, 145, 64, 42), (207, 141, 62, 44), (594, 226, 26, 38), (810, 370, 38, 30)]},
    3: {"style": "market", "floor": [
        (0, 280, 305, 84), (110, 340, 185, 165), (250, 280, 392, 84),
        (330, 98, 430, 207), (610, 280, 350, 84), (640, 340, 245, 175)],
        "blocks": [(354, 122, 68, 48), (454, 122, 68, 48), (554, 122, 68, 48),
                   (670, 350, 45, 38), (145, 355, 42, 34), (800, 155, 40, 42)]},
    4: {"style": "library", "floor": [
        (0, 284, 960, 72), (112, 132, 205, 199), (360, 329, 240, 202),
        (652, 120, 210, 207)],
        "blocks": [(128, 145, 35, 63), (172, 145, 35, 63), (270, 145, 25, 67),
                   (678, 138, 36, 66), (722, 138, 36, 66), (810, 138, 30, 66),
                   (395, 478, 52, 22), (525, 478, 52, 22)]},
    5: {"style": "hospital", "floor": [
        (0, 280, 960, 76), (115, 338, 300, 192), (367, 203, 220, 130),
        (620, 338, 275, 192)],
        "blocks": [(128, 365, 78, 30), (285, 455, 78, 30), (678, 365, 78, 30),
                   (790, 455, 72, 30), (402, 214, 24, 38), (548, 214, 24, 38)]},
    6: {"style": "theatre", "floor": [
        (0, 284, 215, 80), (165, 246, 630, 236), (748, 284, 212, 80),
        (252, 88, 456, 191)],
        "blocks": [(292, 292, 25, 24), (356, 292, 25, 24), (420, 292, 25, 24),
                   (548, 292, 25, 24), (612, 292, 25, 24), (676, 292, 25, 24),
                   (325, 405, 25, 24), (390, 405, 25, 24), (550, 405, 25, 24), (615, 405, 25, 24)]},
    7: {"style": "lake", "floor": [
        (0, 280, 320, 78), (142, 128, 180, 192), (266, 292, 430, 60),
        (390, 334, 200, 204), (625, 280, 335, 78), (657, 128, 205, 192)],
        "blocks": [(162, 148, 24, 28), (270, 156, 22, 24), (692, 150, 24, 24), (812, 165, 22, 27)]},
    8: {"style": "house", "floor": [
        (0, 284, 960, 74), (112, 232, 222, 190), (356, 88, 268, 237),
        (356, 340, 268, 184), (640, 232, 232, 190)],
        "blocks": [(135, 251, 52, 28), (274, 254, 42, 30), (380, 362, 64, 32),
                   (555, 364, 48, 31), (674, 251, 52, 28), (804, 251, 48, 30)]},
    9: {"style": "archive", "floor": [
        (0, 284, 270, 72), (128, 112, 190, 210), (248, 284, 464, 72),
        (378, 337, 226, 198), (650, 112, 215, 210), (700, 284, 260, 72)],
        "blocks": [(145, 130, 30, 72), (182, 130, 30, 72), (275, 130, 26, 72),
                   (676, 130, 30, 72), (714, 130, 30, 72), (814, 130, 27, 72),
                   (407, 465, 33, 31), (548, 465, 33, 31)]},
    10: {"style": "final", "floor": [
        (0, 280, 252, 80), (196, 198, 566, 246), (380, 84, 220, 154),
        (112, 338, 260, 174), (590, 338, 265, 174), (728, 280, 232, 80)],
        "blocks": [(270, 236, 30, 46), (670, 236, 30, 46), (175, 445, 30, 36),
                   (795, 445, 28, 34)]},
}


class AudioEngine:
    """Audio locale: musica in loop, effetti e brevi battute vocali italiane."""
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir) / "luce_sommersa_assets"
        self.music_name = None
        self.enabled = True
        self.muted = False
        self.music_volume = 0.28
        self.sounds = {}
        self.voices = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.voice_channel = pygame.mixer.Channel(15)
            for name in ("pickup", "talk", "gate", "wrong", "step", "final"):
                path = self.base_dir / "sfx" / f"{name}.wav"
                if path.exists():
                    self.sounds[name] = pygame.mixer.Sound(str(path))
            for sound in self.sounds.values():
                sound.set_volume(0.45)
        except pygame.error:
            self.enabled = False

    def set_music(self, filename):
        if not self.enabled or self.music_name == filename:
            return
        path = self.base_dir / "music" / filename
        if not path.exists():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
            pygame.mixer.music.play(-1, fade_ms=650)
            self.music_name = filename
        except pygame.error:
            pass

    def toggle_mute(self):
        self.muted = not self.muted
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
                if self.muted and hasattr(self, "voice_channel"):
                    self.voice_channel.stop()
            except pygame.error:
                pass
        return self.muted

    def play_sfx(self, name):
        if self.enabled and not self.muted and name in self.sounds:
            try:
                self.sounds[name].play()
            except pygame.error:
                pass

    def play_line_voice(self, speaker, text):
        if not self.enabled or self.muted:
            return
        digest = hashlib.sha1((speaker + "\0" + text).encode("utf-8")).hexdigest()[:14]
        filename = digest + ".ogg"
        path = self.base_dir / "voices" / "dialogue" / filename
        if not path.exists():
            self.play_sfx("talk")
            return
        try:
            if filename not in self.voices:
                self.voices[filename] = pygame.mixer.Sound(str(path))
                self.voices[filename].set_volume(0.88)
            self.voice_channel.play(self.voices[filename])
        except pygame.error:
            self.play_sfx("talk")

    def play_voice(self, filename):
        if not self.enabled or self.muted:
            return
        path = self.base_dir / "voices" / filename
        if not path.exists():
            return
        try:
            if filename not in self.voices:
                self.voices[filename] = pygame.mixer.Sound(str(path))
                self.voices[filename].set_volume(0.88)
            self.voice_channel.play(self.voices[filename])
        except pygame.error:
            pass


class Particle:
    def __init__(self, room, initial=False):
        self.reset(room, initial)

    def reset(self, room, initial=False):
        self.x = random.uniform(12, WIDTH - 12)
        self.y = random.uniform(12, HEIGHT - 12) if initial else HEIGHT + random.randint(2, 70)
        self.room = room
        self.size = random.choice((1, 1, 2, 2, 3))
        self.speed = random.uniform(8, 24)
        self.drift = random.uniform(-9, 9)
        self.phase = random.uniform(0, math.tau)
        self.color = PALETTES[room]["dust"]
        self.alpha = random.randint(45, 145)

    def update(self, dt, room):
        if room != self.room:
            self.reset(room, True)
        self.phase += dt * 1.2
        self.y -= self.speed * dt
        self.x += (self.drift + math.sin(self.phase) * 5) * dt
        if self.y < -4 or self.x < -8 or self.x > WIDTH + 8:
            self.reset(room)

    def draw(self, surface):
        c = tuple(int(v * (0.55 + 0.45 * math.sin(self.phase))) for v in self.color)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Luce sommersa — una storia da attraversare")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.audio = AudioEngine(Path(__file__).resolve().parent)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusansmono", 17)
        self.small_font = pygame.font.SysFont("dejavusansmono", 13)
        self.medium_font = pygame.font.SysFont("dejavusansmono", 23, bold=True)
        self.big_font = pygame.font.SysFont("dejavusansmono", 42, bold=True)
        self.tiny_font = pygame.font.SysFont("dejavusansmono", 11)
        self.glow_cache = {}
        self.vignette = self.make_vignette()
        self.backgrounds = [self.build_background(i) for i in range(12)]
        self.extra_maps = {chapter: self.build_extra_map(chapter) for chapter in EXTRA_LAYOUTS}
        self.particles = [Particle(0, True) for _ in range(75)]
        self.reset_game()

    def build_extra_map(self, chapter):
        """Renderizza una mappa distinta, con architettura e decorazioni proprie."""
        layout = EXTRA_LAYOUTS[chapter]
        style = layout["style"]
        palette = PALETTES[chapter + 1]
        rng = random.Random(7100 + chapter)
        bg = pygame.Surface((WIDTH, HEIGHT)).convert()
        if style == "lake":
            bg.fill((5, 24, 39))
            for i in range(24):
                yy = 28 + i * 25
                pygame.draw.line(bg, (9, 39 + (i % 3) * 3, 58), (0, yy), (WIDTH, yy + 8), 1)
            pygame.draw.ellipse(bg, (7, 35, 51), (82, 65, 790, 510))
            pygame.draw.ellipse(bg, (13, 54, 67), (115, 91, 725, 454), 2)
            for i in range(30):
                x = rng.randint(20, WIDTH - 20)
                y = rng.randint(28, HEIGHT - 28)
                pygame.draw.line(bg, (16, 60, 74), (x, y), (x + rng.randint(5, 22), y + 2), 1)
        elif style == "final":
            bg.fill((5, 8, 24))
            for _ in range(150):
                x, y = rng.randrange(WIDTH), rng.randrange(HEIGHT)
                c = rng.choice([(34, 47, 83), (63, 42, 88), (25, 62, 78)])
                bg.set_at((x, y), c)
            for x in range(85, WIDTH, 160):
                pygame.draw.line(bg, (20, 30, 54), (x, 0), (x - 80, HEIGHT), 1)
        else:
            bg.fill(tuple(max(0, c // 3) for c in palette["wall"]))
            # Piccoli dettagli nel vuoto fuori dalle stanze danno profondita.
            for _ in range(90):
                x, y = rng.randrange(WIDTH), rng.randrange(HEIGHT)
                bg.set_at((x, y), tuple(max(0, c // 2) for c in palette["line"]))

        floors = [pygame.Rect(*r) for r in layout["floor"]]
        # Prima le spallette, poi i pavimenti: le sovrapposizioni formano corridoi continui.
        for rect in floors:
            wall_rect = rect.inflate(16, 16)
            pygame.draw.rect(bg, tuple(max(0, c - 7) for c in palette["wall"]), wall_rect)
            pygame.draw.rect(bg, palette["line"], wall_rect, 2)
            pygame.draw.line(bg, tuple(min(255, c + 13) for c in palette["wall"]),
                             wall_rect.topleft, (wall_rect.right - 1, wall_rect.top), 2)
        for ri, rect in enumerate(floors):
            pygame.draw.rect(bg, palette["floor"], rect)
            for gy in range(rect.top // TILE, (rect.bottom + TILE - 1) // TILE):
                for gx in range(rect.left // TILE, (rect.right + TILE - 1) // TILE):
                    cell = pygame.Rect(gx * TILE, gy * TILE, TILE, TILE).clip(rect)
                    if cell.width <= 0 or cell.height <= 0:
                        continue
                    shade = palette["floor2"] if rng.random() < 0.24 else palette["floor"]
                    pygame.draw.rect(bg, shade, cell)
                    # Fughe diverse da quelle delle prime tre stanze.
                    if style in ("library", "archive"):
                        pygame.draw.line(bg, palette["line"], (cell.left + 3, cell.bottom - 3),
                                         (cell.right - 3, cell.bottom - 3), 1)
                    elif style in ("market", "house"):
                        pygame.draw.rect(bg, palette["line"], cell, 1)
                    elif style == "lake":
                        if (gx + gy) % 3 == 0:
                            pygame.draw.line(bg, (36, 84, 94), (cell.left + 5, cell.top + 8),
                                             (cell.left + 20, cell.top + 8), 1)
                    elif style == "final":
                        if rng.random() < 0.14:
                            pygame.draw.line(bg, (77, 76, 125), (cell.left + 5, cell.top + 5),
                                             (cell.left + 16, cell.top + 15), 1)
                    else:
                        pygame.draw.rect(bg, palette["line"], cell, 1)
            pygame.draw.rect(bg, palette["line"], rect, 2)

        # Architetture specifiche del capitolo: sono disegnate nella mappa, non riutilizzate.
        def rect(x, y, w, h, color, border=None, width=1, radius=0):
            pygame.draw.rect(bg, color, (x, y, w, h), border_radius=radius)
            if border:
                pygame.draw.rect(bg, border, (x, y, w, h), width, border_radius=radius)
        def line(a, b, color, width=2):
            pygame.draw.line(bg, color, a, b, width)

        if style == "bells":
            # Facciate della citta, finestre illuminate e campane appese sopra la piazza.
            for x, y, w, h in [(112, 145, 64, 42), (207, 141, 62, 44), (606, 225, 24, 38)]:
                rect(x, y, w, h, (12, 24, 42), palette["glow"], 2)
                pygame.draw.polygon(bg, (41, 43, 73), [(x-5,y+2),(x+w//2,y-15),(x+w+5,y+2)])
                for wx in range(x + 12, x + w - 5, 20):
                    rect(wx, y + 12, 8, 11, (255, 210, 132), (255, 233, 175))
            for x, y in [(215, 205), (480, 145), (760, 405)]:
                pygame.draw.line(bg, (62, 77, 108), (x, y - 48), (x, y - 17), 3)
                pygame.draw.circle(bg, (255, 221, 145), (x, y - 10), 8, 2)
                pygame.draw.arc(bg, palette["glow"], (x-8, y-18, 16, 16), math.pi, 2*math.pi, 2)
        elif style == "market":
            awnings = [(354,122,68,48),(454,122,68,48),(554,122,68,48),(670,350,45,38),(145,355,42,34)]
            awn_colors = [(226,99,129),(88,207,202),(244,190,100),(153,126,244)]
            for i, (x,y,w,h) in enumerate(awnings):
                c = awn_colors[i % len(awn_colors)]
                rect(x,y,w,h,(35,26,51),c,2)
                for xx in range(x+4,x+w-2,12):
                    pygame.draw.polygon(bg, c if (xx//12)%2 else tuple(max(0,v-40) for v in c),
                                        [(xx,y),(min(xx+12,x+w-2),y),(min(xx+10,x+w-2),y+10),(xx+2,y+10)])
                line((x+5,y+h-7),(x+w-5,y+h-7),(238,215,173),2)
            for x,y in [(700,180),(230,410),(730,450)]:
                pygame.draw.circle(bg,(255,225,150),(x,y),20,1)
        elif style == "library":
            # Scaffali alti, scale e tavoli da lettura con corridoi aperti tra loro.
            for x,y,w,h in [(128,145,35,63),(172,145,35,63),(270,145,25,67),
                            (678,138,36,66),(722,138,36,66),(810,138,30,66)]:
                rect(x,y,w,h,(29,19,45),(139,91,133),2)
                for yy in range(y+10,y+h-4,12):
                    line((x+4,yy),(x+w-4,yy),(194,135,161),2)
                pygame.draw.circle(bg,(252,205,138),(x+w//2,y+5),2)
            rect(395,478,52,22,(38,26,53),(164,116,166),2)
            rect(525,478,52,22,(38,26,53),(164,116,166),2)
            for x,y in [(235,235),(485,430),(740,210)]:
                pygame.draw.circle(bg,palette["glow"],(x,y),14,1)
        elif style == "hospital":
            # Reparti e letti riconoscibili, con monitor e tende divisorie.
            for x,y in [(128,365),(285,455),(678,365),(790,455)]:
                rect(x,y,78,30,(48,57,82),(115,153,174),2,3)
                rect(x+7,y+4,19,13,(173,199,207),(222,236,233),1,3)
                line((x+5,y+24),(x+72,y+24),(19,30,53),2)
                line((x+9,y+30),(x+9,y+37),(115,153,174),2)
                line((x+68,y+30),(x+68,y+37),(115,153,174),2)
            for x in (402,548):
                line((x,212),(x,256),(134,169,191),2)
                rect(x-13,212,26,17,(10,24,41),(103,232,220),2)
                pygame.draw.circle(bg,(103,236,217),(x,220),2)
            for x in (95,850):
                rect(x,293,25,42,(19,33,53),(98,123,158),1)
                line((x+6,301),(x+18,301),palette["glow"],2)
        elif style == "theatre":
            # Palco profondo con boccascena e file di poltrone, non una sala vuota.
            rect(278,100,404,138,(39,16,40),(166,66,111),2)
            for x in range(290,680,25):
                pygame.draw.polygon(bg,(109,34,75),[(x,100),(x+15,100),(x+22,235),(x+5,235)])
            rect(310,145,340,82,(20,14,34),(255,184,126),2)
            pygame.draw.ellipse(bg,(255,184,126),(445,159,70,52),2)
            for yy in (300,345,390,435):
                for xx in (285,335,385,575,625,675):
                    rect(xx,yy,22,18,(46,26,50),(142,88,121),2,3)
            line((185,258),(185,466),(175,93,130),3)
            line((775,258),(775,466),(175,93,130),3)
        elif style == "lake":
            # Acqua visibile tra isole e passerelle di legno; piccoli pontili.
            for x,y,w,h in [(82,173,34,16),(320,405,28,13),(610,177,36,14),(864,400,32,12)]:
                pygame.draw.ellipse(bg,(10,43,62),(x,y,w,h))
                pygame.draw.ellipse(bg,(55,125,137),(x,y,w,h),1)
            for x,y in [(230,200),(490,440),(755,200)]:
                pygame.draw.circle(bg,(60,142,153),(x,y),26,1)
                pygame.draw.circle(bg,(103,236,217),(x,y),17,1)
            for x in range(302,660,24):
                rect(x,310,17,23,(44,60,75),(100,164,167),1)
        elif style == "house":
            # Una piantina domestica: finestre, camino, tappeti, divani e armadietti.
            for x in (145,674):
                rect(x,249,45,38,(20,37,51),(151,204,206),2)
                line((x+22,250),(x+22,286),(151,204,206),1)
                line((x,268),(x+45,268),(151,204,206),1)
            rect(425,110,130,48,(31,22,40),(234,155,128),2)
            rect(450,124,80,25,(65,40,50),(255,178,117),2)
            rect(386,365,58,30,(44,36,57),(173,119,158),2,5)
            rect(555,365,48,31,(44,36,57),(173,119,158),2,5)
            rect(400,436,150,28,(57,39,57),(195,149,158),2,3)
            rect(430,441,22,18,(153,95,118),(255,194,176),1,3)
            rect(507,441,22,18,(153,95,118),(255,194,176),1,3)
            for x in (160,800):
                pygame.draw.circle(bg,(255,207,139),(x,316),12,1)
        elif style == "archive":
            # Scaffali stretti, ripiani numerati e registri ordinati per data.
            for x,y,w,h in [(145,130,30,72),(182,130,30,72),(275,130,26,72),
                            (676,130,30,72),(714,130,30,72),(814,130,27,72)]:
                rect(x,y,w,h,(25,23,48),(123,103,155),2)
                for yy in range(y+8,y+h-2,12):
                    line((x+4,yy),(x+w-4,yy),(184,150,194),2)
                draw_label = str((x+y)//17 % 10)
                # Numeri incisi sui dorsi, disegnati con segni geometrici.
                pygame.draw.circle(bg,(255,199,130),(x+w//2,y+h-8),2)
            for x in (407,548):
                rect(x,465,33,31,(35,30,54),(157,124,163),2)
                for i in range(3):
                    line((x+5+i*9,469),(x+5+i*9,491),(202,175,205),1)
        elif style == "final":
            # Piattaforme scheggiate e simboli sospesi in un vuoto stellato.
            for poly in [[(400,91),(586,91),(602,124),(582,225),(397,225),(376,153)],
                         [(130,356),(342,356),(363,386),(350,494),(129,494),(105,430)],
                         [(610,356),(831,356),(849,391),(838,492),(610,492),(584,420)]]:
                pygame.draw.polygon(bg,(24,30,58),poly,2)
                pygame.draw.polygon(bg,(103,90,145),poly,1)
            for x,y in [(270,236),(670,236),(175,445),(795,445)]:
                pts=[(x,y-20),(x+10,y),(x,y+20),(x-10,y)]
                pygame.draw.polygon(bg,(65,78,133),pts)
                pygame.draw.polygon(bg,(186,153,255),pts,1)
            for x in range(285,700,82):
                pygame.draw.circle(bg,(116,205,222),(x,270+int(4*math.sin(x))),2)

        # I blocchi solidi vengono definiti nello stesso schema usato per la collisione.
        for x,y,w,h in layout["blocks"]:
            pygame.draw.rect(bg,(6,10,24),(x,y,w,h),border_radius=2)
            pygame.draw.rect(bg,palette["line"],(x,y,w,h),1,border_radius=2)
        return bg

    def is_walkable_extra(self, x, y):
        """Collisioni reali: si cammina nei pavimenti collegati, non dentro muri/acqua."""
        layout = EXTRA_LAYOUTS.get(self.chapter)
        if not layout:
            return True
        point = (int(x), int(y))
        if not any(pygame.Rect(*area).collidepoint(point) for area in layout["floor"]):
            return False
        for area in layout["blocks"]:
            if pygame.Rect(*area).inflate(7, 7).collidepoint(point):
                return False
        return True

    def reset_game(self):
        self.room = 0
        self.player = [82.0, 530.0]
        self.facing = (1, 0)
        self.walk_time = 0.0
        self.started = False
        self.ending = False
        self.dialogue = None
        self.dialogue_index = 0
        self.dialogue_chars = 0.0
        self.dialogue_tag = None
        self.dialogue_speed = 32.0
        self.room_title_timer = 0.0
        self.flash_timer = 0.0
        self.hint_text = ""
        self.hint_timer = 0.0
        self.gate_hint_seen = False
        self.first_echo_seen = False
        self.pip_spoken = False
        self.has_note = False
        self.nia_spoken = False
        self.rune_progress = 0
        self.rune_touch = [False, False, False]
        self.puzzle_done = False
        self.node_awake = False
        self.node_calm = False
        self.battle_active = False
        self.battle_phase = "attack"
        self.phase_timer = 3.1
        self.bullet_timer = 0.0
        self.wave_number = 0
        self.bullets = []
        self.heart = [480.0, 346.0]
        self.battle_lives = 3
        self.listen_count = 0
        self.listened_this_calm = False
        self.battle_hit_cooldown = 0.0
        self.battle_flash = 0.0
        self.attack_label_timer = 0.0
        self.chapter = 1
        self.extra_progress = 0
        self.extra_found = set()
        self.extra_touch = set()
        self.extra_ready = set()
        self.extra_spoken = set()
        self.extra_interacted = set()
        self.extra_voice_played = set()
        self.step_sound_timer = 0.0
        self.started = False
        self.audio.set_music("ch01.ogg")

    def make_vignette(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Ombra ai bordi, senza coprire il centro della scena.
        for i in range(70):
            alpha = int(1 + (i / 69) ** 2 * 3)
            pygame.draw.rect(overlay, (0, 0, 8, alpha), (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 1)
        return overlay

    def glow_surface(self, color, radius, max_alpha=42):
        key = (color, radius, max_alpha)
        if key in self.glow_cache:
            return self.glow_cache[key]
        s = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        center = (radius + 1, radius + 1)
        steps = 12
        for i in range(steps, 0, -1):
            r = max(1, int(radius * i / steps))
            alpha = max(1, int(max_alpha * (1 - i / (steps + 2)) ** 2 * 1.9))
            pygame.draw.circle(s, (*color, min(255, alpha)), center, r)
        self.glow_cache[key] = s
        return s

    def glow(self, x, y, color, radius=55, alpha=45):
        img = self.glow_surface(color, radius, alpha)
        self.screen.blit(img, (int(x - img.get_width() / 2), int(y - img.get_height() / 2)))

    def build_background(self, room):
        rng = random.Random(1900 + room)
        p = PALETTES[room]
        bg = pygame.Surface((WIDTH, HEIGHT)).convert()
        bg.fill(p["floor"])
        for gy in range(HEIGHT // TILE):
            for gx in range(WIDTH // TILE):
                rect = pygame.Rect(gx * TILE, gy * TILE, TILE, TILE)
                border = gx in (0, WIDTH // TILE - 1) or gy in (0, HEIGHT // TILE - 1)
                side_door = gy in (9, 10) and (gx in (0, WIDTH // TILE - 1))
                top_door = room == 2 and gx in (14, 15) and gy == 0
                if border and not side_door and not top_door:
                    shade = tuple(min(255, max(0, c + rng.randint(-5, 7))) for c in p["wall"])
                    pygame.draw.rect(bg, shade, rect)
                    pygame.draw.rect(bg, p["line"], rect, 1)
                    pygame.draw.line(bg, tuple(min(255, c + 14) for c in p["wall"]), rect.topleft, (rect.right - 1, rect.top), 2)
                    pygame.draw.line(bg, tuple(max(0, c - 8) for c in p["wall"]), (rect.left, rect.bottom - 2), (rect.right - 1, rect.bottom - 2), 2)
                else:
                    shade = p["floor2"] if rng.random() < 0.23 else p["floor"]
                    pygame.draw.rect(bg, shade, rect)
                    pygame.draw.rect(bg, (*p["line"],), rect, 1)
                    if rng.random() < 0.18:
                        sx = rect.x + rng.randint(5, 26)
                        sy = rect.y + rng.randint(5, 26)
                        color = tuple(int(c * 0.76) for c in p["line"])
                        pygame.draw.line(bg, color, (sx, sy), (sx + rng.randint(-5, 5), sy + rng.randint(2, 7)), 1)
                    if room == 1 and rng.random() < 0.065:
                        pygame.draw.line(bg, (45, 69, 110), (rect.x + 6, rect.y + 7), (rect.x + 25, rect.y + 22), 1)
                    if room == 2 and rng.random() < 0.09:
                        pygame.draw.line(bg, (89, 32, 83), (rect.x + 4, rect.y + 27), (rect.x + 14, rect.y + 14), 1)
        # Decorazioni statiche, disegnate una volta sola.
        if room == 0:
            for x, y in ((125, 170), (830, 175), (310, 540), (595, 135), (860, 520)):
                pygame.draw.circle(bg, (25, 52, 66), (x, y), 18)
                pygame.draw.circle(bg, (35, 72, 82), (x, y), 13, 2)
            for x in range(120, 880, 160):
                pygame.draw.line(bg, (31, 57, 73), (x, 70), (x + 24, 83), 2)
        elif room == 1:
            for x, y in ((145, 175), (815, 160), (820, 505), (125, 510), (500, 100)):
                pygame.draw.polygon(bg, (28, 49, 83), [(x, y - 24), (x + 15, y), (x, y + 24), (x - 15, y)])
                pygame.draw.polygon(bg, (72, 91, 145), [(x, y - 15), (x + 9, y), (x, y + 15), (x - 9, y)], 1)
        else:
            # Cerchio spezzato nel pavimento: il Nodo dorme al centro.
            pygame.draw.circle(bg, (33, 20, 48), (480, 326), 128, 2)
            pygame.draw.circle(bg, (46, 23, 58), (480, 326), 99, 1)
            for a in range(0, 360, 30):
                x1 = 480 + math.cos(math.radians(a)) * 108
                y1 = 326 + math.sin(math.radians(a)) * 108
                x2 = 480 + math.cos(math.radians(a)) * 124
                y2 = 326 + math.sin(math.radians(a)) * 124
                pygame.draw.line(bg, (83, 36, 82), (x1, y1), (x2, y2), 2)
        return bg

    def start_dialogue(self, lines, tag=None):
        self.dialogue = lines
        self.dialogue_index = 0
        self.dialogue_chars = 0.0
        self.dialogue_tag = tag
        if lines:
            self.audio.play_line_voice(lines[0][0], lines[0][1])

    def finish_dialogue(self):
        tag = self.dialogue_tag
        self.dialogue = None
        self.dialogue_tag = None
        if tag == "battle_intro":
            self.battle_active = True
            self.battle_phase = "attack"
            self.phase_timer = 3.0
            self.bullet_timer = 0.0
            self.bullets.clear()
            self.heart = [480.0, 350.0]
            self.battle_lives = 3
            self.listen_count = 0
            self.wave_number = 0
        elif tag == "retry_battle":
            self.battle_active = True
            self.battle_phase = "attack"
            self.phase_timer = 2.7
            self.bullet_timer = 0.0
            self.bullets.clear()
            self.heart = [480.0, 350.0]
            self.battle_lives = 3
            self.listen_count = 0
            self.wave_number = 0
        elif tag == "battle_win":
            self.node_calm = True
            self.room_title_timer = 2.3
        elif tag == "opening":
            self.started = True
            self.room_title_timer = 2.6
        elif tag == "extra_complete":
            self.extra_ready.add(self.chapter)
            self.audio.play_sfx("gate")
            self.show_hint("Il passaggio si apre. Prosegui verso est.", 2.3)
        elif tag == "true_ending":
            self.ending = True
            self.audio.set_music("ch10.ogg")
            self.audio.play_sfx("final")

    def advance_dialogue(self):
        if not self.dialogue:
            return
        line = self.dialogue[self.dialogue_index][1]
        if self.dialogue_chars < len(line):
            self.dialogue_chars = len(line)
            return
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue):
            self.finish_dialogue()
        else:
            self.dialogue_chars = 0.0
            speaker, text = self.dialogue[self.dialogue_index]
            self.audio.play_line_voice(speaker, text)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if key == pygame.K_m:
            muted = self.audio.toggle_mute()
            self.show_hint("Audio disattivato" if muted else "Audio attivato", 1.3)
            return
        if not self.started:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_e):
                self.started = True
                self.start_dialogue([
                    ("VOCE", "Ti svegli su una banchina che non appare su nessuna mappa."),
                    ("VOCE", "Non ricordi il viaggio. Ricordi soltanto un suono, come una campanella sotto l'acqua."),
                    ("VOCE", "A est c'e una porta spenta. Forse questo posto puo risponderti.")
                ], "opening")
            return
        if self.ending:
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_game()
            return
        if self.dialogue:
            if key in (pygame.K_z, pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                self.advance_dialogue()
            return
        if self.battle_active:
            if key in (pygame.K_e, pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
                self.listen_during_battle()
            return
        if key in (pygame.K_e, pygame.K_z, pygame.K_RETURN, pygame.K_SPACE):
            self.interact()

    def interact(self):
        if self.room >= 3:
            self.interact_extra()
            return
        px, py = self.player
        candidates = []
        if self.room == 0:
            candidates = [
                ("targa", "Targa", 235, 412),
                ("pip", "Pip", 500, 322),
                ("porta", "Porta che ascolta", 884, 320),
            ]
        elif self.room == 1:
            candidates = [
                ("nia", "Nia", 160, 470),
                ("specchio", "Specchio incrinato", 805, 478),
            ]
        elif self.room == 2 and not self.node_awake:
            candidates = [("segni", "Segni sul pavimento", 480, 455)]
        close = [(distance((px, py), (x, y)), key, name) for key, name, x, y in candidates]
        close = [item for item in close if item[0] < 62]
        if not close:
            self.show_hint("Non c'e niente a portata di mano.", 1.1)
            return
        _, target, _ = min(close, key=lambda item: item[0])
        self.audio.play_sfx("talk")
        if target == "targa":
            self.start_dialogue([
                ("TARGA", "BINARIO ZERO. Ultima fermata: cio che non hai detto."),
                ("TARGA", "Qualcuno ha inciso sotto: 'Ascoltare non significa essere d'accordo.'")
            ])
        elif target == "pip":
            if not self.pip_spoken:
                self.pip_spoken = True
                self.start_dialogue([
                    ("PIP", "Oh. Un visitatore che fa ancora rumore."),
                    ("PIP", "Sono Pip. Questa stazione conserva le cose che il mondo smette di ascoltare."),
                    ("PIP", "La porta a est si apre con una nota vera. Senti quella piccola vibrazione? Cercala sul pavimento.")
                ])
            else:
                self.start_dialogue([
                    ("PIP", "La scheggia e vicina. Non serve prenderla con le mani: basta passarle accanto."),
                    ("PIP", "E quando la porta si apre, non correre. I posti dimenticati hanno parecchio da raccontare.")
                ])
        elif target == "porta":
            if self.has_note and self.pip_spoken:
                self.change_room(1, 30, 320)
            else:
                text = "La porta vibra, ma non si apre. Manca una nota." if self.pip_spoken else "La porta resta muta. Forse qualcuno qui sa come parlarle."
                self.start_dialogue([("PORTA", text)])
        elif target == "nia":
            if not self.nia_spoken:
                self.nia_spoken = True
                self.start_dialogue([
                    ("NIA", "Non puoi rompere il vetro. Puoi solo ricordargli come brillare."),
                    ("NIA", "Cammina sulle tre note nell'ordine dei riflessi: azzurro, oro, rosa."),
                    ("NIA", "Non c'e fretta. Se sbagli, il giardino aspettera.")
                ])
            else:
                self.start_dialogue([("NIA", "Azzurro. Oro. Rosa. Lascia che siano i tuoi passi a dirlo.")])
        elif target == "specchio":
            if self.puzzle_done:
                self.start_dialogue([("SPECCHIO", "Il tuo riflesso ti saluta un secondo prima che tu ti muova."), ("SPECCHIO", "Poi torna al suo posto, come se non fosse successo niente.")])
            else:
                self.start_dialogue([("SPECCHIO", "Tre luci aspettano sul pavimento. Lo specchio non riflette i colori: li ricorda.")])
        elif target == "segni":
            self.start_dialogue([("PAVIMENTO", "Una frase corre lungo le crepe: 'La paura fa rumore. La risposta non deve farne di piu.'")])

    def show_hint(self, text, duration=1.7):
        self.hint_text = text
        self.hint_timer = duration

    def change_room(self, room, x, y):
        self.room = room
        self.room_title_timer = 2.8
        self.hint_timer = 0
        self.flash_timer = 0.16
        self.particles = [Particle(room, True) for _ in range(75)]
        if room >= 3:
            self.chapter = room - 1
            # Ogni nuova mappa ha geometrie proprie: non riutilizzare alla cieca
            # le coordinate d'uscita della stanza precedente. Il vecchio ingresso
            # del capitolo 2 era (72, 548), fuori dal pavimento: il player restava
            # bloccato nel vuoto. Preferiamo un ingresso sul corridoio ovest e
            # manteniamo un fallback nel caso una mappa venga modificata in futuro.
            spawn_candidates = [(x, y), (36, 320), (42, 320), (36, 310), (36, 330), (56, 320)]
            spawn = next(((sx, sy) for sx, sy in spawn_candidates
                          if self.is_walkable_extra(sx, sy)), None)
            if spawn is None:
                layout = EXTRA_LAYOUTS.get(self.chapter, {})
                for area in layout.get("floor", []):
                    sx = area[0] + min(24, max(1, area[2] // 2))
                    sy = area[1] + area[3] // 2
                    if self.is_walkable_extra(sx, sy):
                        spawn = (sx, sy)
                        break
            self.player = [float(spawn[0]), float(spawn[1])] if spawn else [36.0, 320.0]
            self.audio.set_music(f"ch{self.chapter:02d}.ogg")
            self.start_extra_chapter(self.chapter)
            return
        self.player = [float(x), float(y)]
        if room == 2 and not self.node_awake:
            self.node_awake = True
            self.start_dialogue([
                ("VOCE", "La camera si restringe attorno ai tuoi passi. Le pareti trattengono il fiato."),
                ("VOCE", "Un nodo di buio si stacca dal soffitto. Non sembra arrabbiato. Sembra terrorizzato."),
                ("NODO", "Non avvicinarti. Ogni volta che qualcuno ha paura, mi chiedono di diventare un mostro."),
                ("NODO", "Resta qui. Schiva il rumore. Quando arriva il silenzio, premi E per ascoltare.")
            ], "battle_intro")

    def move_player(self, dx, dy):
        x, y = self.player
        nx, ny = x + dx, y + dy
        if self.room >= 3:
            if dx and nx < 14:
                nx = 20
            if dx and nx > WIDTH - 14:
                if 286 <= ny <= 354:
                    if self.chapter == 10:
                        self.show_hint("Non c'e una via d'uscita. Prima parla con la figura al centro.", 2.0)
                        nx = WIDTH - 31
                    elif self.chapter in self.extra_ready:
                        self.change_room(self.room + 1, 36, 320)
                        return
                    else:
                        self.show_hint("Il passaggio aspetta che tu abbia trovato tutti i frammenti.", 1.8)
                        nx = WIDTH - 31
                else:
                    nx = WIDTH - 20
            if dy and ny < 14:
                ny = 20
            if dy and ny > HEIGHT - 14:
                ny = HEIGHT - 20

            # Movimento con scivolamento lungo gli ostacoli: si puo girare agli
            # angoli, ma non attraversare mobili, scaffali, pareti o vuoto.
            if self.is_walkable_extra(nx, ny):
                pass
            else:
                can_x = self.is_walkable_extra(nx, y)
                can_y = self.is_walkable_extra(x, ny)
                if can_x:
                    ny = y
                elif can_y:
                    nx = x
                else:
                    nx, ny = x, y
            self.player = [nx, ny]
            if abs(dx) + abs(dy) > 0:
                self.walk_time += math.hypot(dx, dy) * 0.1
            return
        if dx:
            if nx < 14:
                if self.room in (1, 2) and 286 <= ny <= 354:
                    if self.room == 1:
                        self.change_room(0, 925, 320)
                    else:
                        self.change_room(1, 925, 320)
                    return
                nx = 20
            if nx > WIDTH - 14:
                if 286 <= ny <= 354:
                    if self.room == 0:
                        if self.has_note and self.pip_spoken:
                            self.change_room(1, 30, 320)
                            return
                        nx = WIDTH - 31
                        if not self.gate_hint_seen:
                            self.gate_hint_seen = True
                            text = "La porta vibra, ma non si apre. Manca ancora una nota." if self.pip_spoken else "La porta resta muta. Cerca qualcuno che possa ascoltarti."
                            self.start_dialogue([("PORTA", text)])
                    elif self.room == 1:
                        if self.puzzle_done:
                            self.change_room(2, 30, 320)
                            return
                        nx = WIDTH - 31
                        self.show_hint("Il giardino non ha ancora completato la sua melodia.", 2.0)
                else:
                    nx = WIDTH - 20
        if dy:
            if ny < 14:
                if self.room == 2 and self.node_calm and 442 <= nx <= 518:
                    self.change_room(3, 72, 548)
                    return
                ny = 20
            if ny > HEIGHT - 14:
                ny = HEIGHT - 20
        self.player = [nx, ny]
        if abs(dx) + abs(dy) > 0:
            self.walk_time += math.hypot(dx, dy) * 0.1

    def update_runes(self):
        if self.room != 1 or self.puzzle_done or self.dialogue:
            return
        runes = [(280, 320), (480, 220), (690, 320)]
        for i, pos in enumerate(runes):
            d = distance(self.player, pos)
            if d > 34:
                self.rune_touch[i] = False
            elif not self.rune_touch[i]:
                self.rune_touch[i] = True
                if i == self.rune_progress:
                    self.audio.play_sfx("pickup")
                    self.rune_progress += 1
                    lines = [
                        [("GIARDINO", "L'azzurro risponde ai tuoi passi.")],
                        [("GIARDINO", "L'oro raccoglie la vibrazione e la manda avanti.")],
                        [("GIARDINO", "Il rosa completa la melodia. Il vetro ricorda come aprirsi.")],
                    ]
                    if self.rune_progress == 3:
                        self.puzzle_done = True
                        self.start_dialogue(lines[i] + [("VOCE", "La via a est si illumina. Hai trovato la sequenza camminandoci dentro.")])
                    else:
                        self.start_dialogue(lines[i])
                    return
                else:
                    self.audio.play_sfx("wrong")
                    self.rune_progress = 0
                    self.show_hint("Le luci si spengono. Riprova: azzurro, oro, rosa.", 2.2)

    def listen_during_battle(self):
        if not self.battle_active:
            return
        if self.battle_phase == "calm":
            if not self.listened_this_calm:
                self.listened_this_calm = True
                self.listen_count += 1
                self.attack_label_timer = 1.4
                if self.listen_count >= 3:
                    self.show_hint("Il rumore si arrende. Non serve colpire.", 1.5)
            else:
                self.show_hint("Hai gia ascoltato questo silenzio.", 0.9)
        else:
            self.show_hint("Aspetta che torni il silenzio.", 0.85)

    def spawn_bullet(self):
        left, top, right, bottom = 300, 245, 660, 438
        mode = self.wave_number % 3
        if mode == 0:
            x = random.uniform(left + 8, right - 8)
            self.bullets.append({"x": x, "y": top - 12, "vx": random.uniform(-13, 13), "vy": random.uniform(105, 155), "r": random.choice((5, 6, 7)), "c": (117, 231, 255)})
        elif mode == 1:
            y = random.uniform(top + 12, bottom - 10)
            from_left = random.choice((True, False))
            x = left - 10 if from_left else right + 10
            vx = random.uniform(128, 168) * (1 if from_left else -1)
            self.bullets.append({"x": x, "y": y, "vx": vx, "vy": random.uniform(-12, 12), "r": 6, "c": (255, 112, 184)})
        else:
            # Frammenti lenti indirizzati verso il cuore: leggibili e schivabili.
            sx = random.choice((left - 8, right + 8))
            sy = random.uniform(top + 12, bottom - 12)
            vx, vy = self.heart[0] - sx, self.heart[1] - sy
            mag = max(1.0, math.hypot(vx, vy))
            speed = random.uniform(105, 132)
            self.bullets.append({"x": sx, "y": sy, "vx": vx / mag * speed, "vy": vy / mag * speed, "r": 7, "c": (255, 190, 97)})
        self.wave_number += 1

    def update_battle(self, dt, keys):
        left, top, right, bottom = 300, 245, 660, 438
        self.battle_hit_cooldown = max(0, self.battle_hit_cooldown - dt)
        self.battle_flash = max(0, self.battle_flash - dt)
        self.attack_label_timer = max(0, self.attack_label_timer - dt)
        speed = 210
        mx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        my = (1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0) - (1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        if mx or my:
            mag = math.hypot(mx, my)
            self.heart[0] += mx / mag * speed * dt
            self.heart[1] += my / mag * speed * dt
        self.heart[0] = clamp(self.heart[0], left + 13, right - 13)
        self.heart[1] = clamp(self.heart[1], top + 13, bottom - 13)
        self.phase_timer -= dt
        if self.battle_phase == "attack":
            self.bullet_timer -= dt
            if self.bullet_timer <= 0:
                self.spawn_bullet()
                self.bullet_timer = 0.34 if self.wave_number < 12 else 0.29
            kept = []
            for b in self.bullets:
                b["x"] += b["vx"] * dt
                b["y"] += b["vy"] * dt
                if left - 25 <= b["x"] <= right + 25 and top - 30 <= b["y"] <= bottom + 30:
                    kept.append(b)
                    if self.battle_hit_cooldown <= 0 and math.hypot(b["x"] - self.heart[0], b["y"] - self.heart[1]) < b["r"] + 8:
                        self.battle_lives -= 1
                        self.battle_hit_cooldown = 0.95
                        self.battle_flash = 0.22
                        self.heart = [clamp(self.heart[0] - 26, left + 13, right - 13), clamp(self.heart[1] + 18, top + 13, bottom - 13)]
                # Gli oggetti fuori dall'arena vengono scartati.
            self.bullets = kept
        else:
            # Piccola pausa leggibile: niente proiettili nel silenzio.
            self.bullets.clear()
        if self.battle_lives <= 0:
            self.battle_active = False
            self.start_dialogue([
                ("NODO", "Il rumore ti respinge, ma non ti cancella."),
                ("VOCE", "Ricomponi il respiro. Questa volta conosci gia il ritmo.")
            ], "retry_battle")
            return
        if self.phase_timer <= 0:
            if self.battle_phase == "attack":
                self.battle_phase = "calm"
                self.phase_timer = 1.85
                self.listened_this_calm = False
                self.bullets.clear()
            else:
                if self.listen_count >= 3:
                    self.battle_active = False
                    self.node_calm = True
                    self.start_dialogue([
                        ("NODO", "...Mi hai sentito davvero."),
                        ("VOCE", "Il Nodo smette di lanciare frammenti. Sotto il buio non c'era rabbia, ma una voce rimasta troppo a lungo senza risposta."),
                        ("VOCE", "Non lo sconfiggi. Gli fai spazio. In alto, una porta si accende.")
                    ], "battle_win")
                    return
                self.battle_phase = "attack"
                self.phase_timer = 3.0
                self.bullet_timer = 0.12

    def update(self, dt, keys):
        for particle in self.particles:
            particle.update(dt, self.room)
        self.room_title_timer = max(0, self.room_title_timer - dt)
        self.flash_timer = max(0, self.flash_timer - dt)
        self.hint_timer = max(0, self.hint_timer - dt)
        if self.dialogue:
            line = self.dialogue[self.dialogue_index][1]
            self.dialogue_chars = min(len(line), self.dialogue_chars + self.dialogue_speed * dt)
            return
        if not self.started or self.ending:
            return
        if self.battle_active:
            self.update_battle(dt, keys)
            return
        dx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        dy = (1 if keys[pygame.K_DOWN] or keys[pygame.K_s] else 0) - (1 if keys[pygame.K_UP] or keys[pygame.K_w] else 0)
        if dx or dy:
            self.step_sound_timer -= dt
            if self.step_sound_timer <= 0:
                self.audio.play_sfx("step")
                self.step_sound_timer = 0.30
            mag = math.hypot(dx, dy)
            speed = 220 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 158
            if dx:
                self.facing = (dx, 0)
            elif dy:
                self.facing = (0, dy)
            self.move_player(dx / mag * speed * dt, dy / mag * speed * dt)
        else:
            self.step_sound_timer = min(self.step_sound_timer, 0.04)
        if self.dialogue:
            return
        if self.room == 0:
            if not self.first_echo_seen and self.player[0] > 310 and self.player[1] < 480:
                self.first_echo_seen = True
                self.start_dialogue([
                    ("VOCE", "I tuoi passi arrivano con un secondo di ritardo."),
                    ("VOCE", "La stazione ti sta ascoltando. O forse sta cercando di ricordare come si fa.")
                ])
            if not self.has_note and distance(self.player, (708, 490)) < 24:
                self.has_note = True
                self.flash_timer = 0.3
                self.audio.play_sfx("pickup")
                self.start_dialogue([
                    ("VOCE", "La scheggia non e una chiave. E un suono solidificato."),
                    ("VOCE", "Per un istante, tutta la stanza ricorda il mare.")
                ])
        elif self.room == 1:
            self.update_runes()
        elif self.room == 2 and not self.node_awake and self.player[0] > 260:
            self.node_awake = True
            self.start_dialogue([
                ("VOCE", "La camera si restringe attorno ai tuoi passi. Le pareti trattengono il fiato."),
                ("NODO", "Non avvicinarti. Ogni volta che qualcuno ha paura, mi chiedono di diventare un mostro."),
                ("NODO", "Schiva il rumore. Quando arriva il silenzio, premi E per ascoltare.")
            ], "battle_intro")
        elif self.room >= 3:
            self.update_extra_world()

    def draw_pip(self, x, y, t):
        bob = math.sin(t * 2.3) * 4
        y += bob
        self.glow(x, y, (69, 221, 235), 54, 43)
        pygame.draw.ellipse(self.screen, (5, 11, 25), (x - 20, y + 14, 40, 12))
        # Mantellina a pixel e testa-lanterna.
        pygame.draw.polygon(self.screen, (34, 83, 113), [(x - 17, y + 1), (x + 17, y + 1), (x + 11, y + 22), (x, y + 27), (x - 11, y + 22)])
        pygame.draw.polygon(self.screen, (62, 135, 159), [(x - 11, y + 4), (x + 11, y + 4), (x + 6, y + 20), (x, y + 22), (x - 6, y + 20)])
        pygame.draw.rect(self.screen, (151, 245, 238), (x - 10, y - 13, 20, 18))
        pygame.draw.rect(self.screen, (216, 255, 237), (x - 6, y - 18, 12, 6))
        pygame.draw.rect(self.screen, (10, 28, 46), (x - 6, y - 7, 4, 5))
        pygame.draw.rect(self.screen, (10, 28, 46), (x + 3, y - 7, 4, 5))
        pygame.draw.rect(self.screen, (242, 255, 213), (x - 5, y - 6, 2, 2))
        pygame.draw.rect(self.screen, (242, 255, 213), (x + 4, y - 6, 2, 2))

    def draw_nia(self, x, y, t):
        bob = math.sin(t * 1.8 + 1) * 2.5
        y += bob
        self.glow(x, y, (167, 139, 255), 43, 32)
        pygame.draw.ellipse(self.screen, (5, 10, 24), (x - 15, y + 15, 30, 9))
        pygame.draw.polygon(self.screen, (73, 66, 132), [(x - 13, y - 2), (x + 13, y - 2), (x + 12, y + 18), (x, y + 23), (x - 12, y + 18)])
        pygame.draw.rect(self.screen, (213, 208, 255), (x - 9, y - 14, 18, 16))
        pygame.draw.rect(self.screen, (246, 225, 255), (x - 6, y - 19, 12, 5))
        pygame.draw.rect(self.screen, (37, 32, 76), (x - 5, y - 8, 3, 4))
        pygame.draw.rect(self.screen, (37, 32, 76), (x + 3, y - 8, 3, 4))

    def draw_player(self):
        x, y = self.player
        moving = self.started and not self.dialogue and not self.battle_active
        bob = abs(math.sin(self.walk_time * 1.25)) * 2 if moving else math.sin(pygame.time.get_ticks() * 0.002) * 1.5
        y += bob
        self.glow(x, y + 3, (74, 226, 243), 33, 25)
        pygame.draw.ellipse(self.screen, (4, 9, 22), (int(x - 14), int(y + 13), 28, 10))
        # Mantello turchese, testa quadrata e occhi luminosi: sprite procedurale.
        pygame.draw.rect(self.screen, (21, 70, 105), (int(x - 12), int(y - 2), 24, 19))
        pygame.draw.rect(self.screen, (35, 137, 157), (int(x - 10), int(y), 20, 15))
        pygame.draw.rect(self.screen, (21, 70, 105), (int(x - 8), int(y + 13), 6, 7))
        pygame.draw.rect(self.screen, (21, 70, 105), (int(x + 2), int(y + 13), 6, 7))
        pygame.draw.rect(self.screen, (183, 255, 240), (int(x - 10), int(y - 17), 20, 17))
        pygame.draw.rect(self.screen, (234, 255, 246), (int(x - 6), int(y - 22), 12, 5))
        pygame.draw.rect(self.screen, (10, 30, 47), (int(x - 6), int(y - 11), 4, 5))
        pygame.draw.rect(self.screen, (10, 30, 47), (int(x + 3), int(y - 11), 4, 5))
        pygame.draw.rect(self.screen, (250, 255, 206), (int(x - 5), int(y - 10), 2, 2))
        pygame.draw.rect(self.screen, (250, 255, 206), (int(x + 4), int(y - 10), 2, 2))
        # La spilla cambia colore quando la nota e stata raccolta.
        pin = (255, 218, 111) if self.has_note else (79, 238, 239)
        pygame.draw.rect(self.screen, pin, (int(x + 4), int(y + 3), 4, 4))

    def draw_sign(self, x, y):
        pygame.draw.ellipse(self.screen, (5, 8, 20), (x - 20, y + 13, 40, 10))
        pygame.draw.rect(self.screen, (61, 73, 85), (x - 17, y - 14, 34, 28))
        pygame.draw.rect(self.screen, (100, 126, 137), (x - 14, y - 11, 28, 22), 2)
        pygame.draw.line(self.screen, (169, 199, 187), (x - 8, y - 5), (x + 7, y - 5), 2)
        pygame.draw.line(self.screen, (169, 199, 187), (x - 8, y), (x + 4, y), 2)
        pygame.draw.line(self.screen, (169, 199, 187), (x - 8, y + 5), (x + 7, y + 5), 2)

    def draw_note(self, t):
        if self.has_note or self.room != 0:
            return
        x, y = 708, 490 + math.sin(t * 2.6) * 4
        self.glow(x, y, (255, 211, 104), 62, 50)
        pygame.draw.polygon(self.screen, (255, 219, 122), [(x, y - 13), (x + 9, y), (x, y + 13), (x - 9, y)])
        pygame.draw.polygon(self.screen, (255, 250, 208), [(x, y - 7), (x + 4, y), (x, y + 7), (x - 4, y)])

    def draw_door(self, t):
        x, y = WIDTH - 18, 320
        if self.room == 0:
            open_now = self.has_note and self.pip_spoken
            color = (89, 230, 211) if open_now else (69, 95, 113)
            self.glow(x - 8, y, color, 70 if open_now else 38, 47 if open_now else 14)
            pygame.draw.rect(self.screen, (7, 13, 28), (x - 25, y - 46, 35, 92))
            pygame.draw.rect(self.screen, color, (x - 24, y - 44, 32, 88), 3)
            pygame.draw.rect(self.screen, (24, 42, 58), (x - 17, y - 34, 18, 68))
            if open_now:
                for k in range(4):
                    xx = x - 14 + k * 5
                    pygame.draw.line(self.screen, (98, 240, 220), (xx, y - 28), (xx, y + 28), 1)
        elif self.room == 1:
            open_now = self.puzzle_done
            color = (183, 144, 255) if open_now else (75, 85, 126)
            self.glow(x - 8, y, color, 62 if open_now else 35, 45 if open_now else 13)
            pygame.draw.rect(self.screen, (7, 13, 28), (x - 25, y - 46, 35, 92))
            pygame.draw.rect(self.screen, color, (x - 24, y - 44, 32, 88), 3)
            pygame.draw.rect(self.screen, (22, 34, 63), (x - 17, y - 34, 18, 68))
            if open_now:
                pygame.draw.line(self.screen, (240, 204, 255), (x - 8, y - 27), (x - 8, y + 27), 2)
        elif self.room == 2 and not self.node_calm:
            # La porta d'uscita e solo una crepa nel muro finche il Nodo non viene ascoltato.
            pygame.draw.line(self.screen, (99, 42, 86), (x - 8, y - 35), (x - 8, y + 34), 2)

    def draw_runes(self, t):
        if self.room != 1:
            return
        positions = [(280, 320), (480, 220), (690, 320)]
        colors = [(94, 230, 255), (255, 211, 116), (255, 123, 209)]
        for i, (x, y) in enumerate(positions):
            active = self.puzzle_done or i < self.rune_progress
            pulse = math.sin(t * 3.1 + i * 1.5) * 3
            self.glow(x, y, colors[i], int(43 + pulse), 35 if active else 20)
            pygame.draw.circle(self.screen, (14, 20, 42), (x, y), 18)
            pygame.draw.circle(self.screen, colors[i] if active else tuple(int(c * 0.45) for c in colors[i]), (x, y), 14, 3)
            pygame.draw.circle(self.screen, colors[i], (x, y), 5 if active else 3)
            # Piccola scia direzionale suggerisce che sono note, non interruttori.
            pygame.draw.arc(self.screen, colors[i], (x - 24, y - 24, 48, 48), math.radians(210), math.radians(315), 2)

    def draw_boss(self, t):
        x, y = 480, 150 + math.sin(t * 1.5) * 5
        core = (255, 103, 174) if not self.node_calm else (132, 224, 232)
        self.glow(x, y, core, 108, 64)
        # Frammenti orbitanti, disegnati come pixel di vetro.
        for i in range(8):
            a = t * 0.65 + i * math.tau / 8
            rx = x + math.cos(a) * (45 + 4 * math.sin(t + i))
            ry = y + math.sin(a) * 24
            pygame.draw.polygon(self.screen, (104, 46, 107), [(rx, ry - 8), (rx + 5, ry), (rx, ry + 8), (rx - 5, ry)])
            pygame.draw.polygon(self.screen, core, [(rx, ry - 5), (rx + 3, ry), (rx, ry + 5), (rx - 3, ry)])
        pygame.draw.polygon(self.screen, (47, 23, 61), [(x - 42, y - 4), (x - 23, y - 37), (x + 19, y - 45), (x + 43, y - 8), (x + 26, y + 29), (x - 14, y + 34)])
        pygame.draw.polygon(self.screen, (117, 46, 102), [(x - 29, y - 7), (x - 16, y - 27), (x + 13, y - 32), (x + 30, y - 5), (x + 18, y + 19), (x - 9, y + 23)])
        pygame.draw.rect(self.screen, (255, 194, 222), (int(x - 12), int(y - 7), 6, 4))
        pygame.draw.rect(self.screen, (255, 194, 222), (int(x + 7), int(y - 7), 6, 4))
        pygame.draw.line(self.screen, (61, 29, 71), (x - 8, y + 9), (x + 8, y + 9), 2)

    def draw_arena(self):
        # Arena a cornice, in sovraimpressione sulla stanza.
        panel = pygame.Surface((404, 236), pygame.SRCALPHA)
        pygame.draw.rect(panel, (5, 6, 20, 225), (0, 0, 404, 236), border_radius=8)
        pygame.draw.rect(panel, (137, 82, 139, 255), (0, 0, 404, 236), 3, border_radius=8)
        pygame.draw.rect(panel, (62, 51, 100, 255), (5, 5, 394, 226), 1, border_radius=6)
        self.screen.blit(panel, (278, 224))
        # Angoli luminosi.
        for x, y in ((282, 228), (678, 228), (282, 456), (678, 456)):
            self.glow(x, y, (239, 110, 192), 20, 20)
            pygame.draw.rect(self.screen, (255, 174, 224), (x - 3, y - 3, 6, 6))
        for b in self.bullets:
            self.glow(b["x"], b["y"], b["c"], 19, 25)
            pygame.draw.circle(self.screen, b["c"], (int(b["x"]), int(b["y"])), b["r"])
            pygame.draw.circle(self.screen, (255, 245, 250), (int(b["x"] - 2), int(b["y"] - 2)), max(1, b["r"] // 3))
        # Cuore del giocatore, senza sprite esterni.
        hx, hy = int(self.heart[0]), int(self.heart[1])
        blink = self.battle_hit_cooldown > 0 and int(pygame.time.get_ticks() / 85) % 2 == 0
        if not blink:
            self.glow(hx, hy, (255, 84, 126), 28, 55)
            pygame.draw.circle(self.screen, (255, 91, 135), (hx - 4, hy - 3), 6)
            pygame.draw.circle(self.screen, (255, 91, 135), (hx + 4, hy - 3), 6)
            pygame.draw.polygon(self.screen, (255, 91, 135), [(hx - 10, hy - 1), (hx + 10, hy - 1), (hx, hy + 11)])
            pygame.draw.circle(self.screen, (255, 220, 230), (hx - 5, hy - 5), 2)
        # UI battaglia: niente livelli, equipaggiamento o menu di statistiche.
        draw_text(self.screen, self.small_font, "NODO DEL SILENZIO", (255, 218, 239), (300, 195))
        for i in range(3):
            color = (255, 100, 147) if i < self.battle_lives else (79, 51, 76)
            pygame.draw.rect(self.screen, color, (610 + i * 14, 197, 9, 9))
        if self.battle_phase == "attack":
            msg = "SCHIVA IL RUMORE"
            color = (255, 170, 207)
        else:
            msg = "SILENZIO — PREMI E PER ASCOLTARE" if not self.listened_this_calm else "HAI ASCOLTATO. RESTA QUI."
            color = (151, 245, 236)
        draw_text(self.screen, self.small_font, msg, color, (480, 476), center=True)
        draw_text(self.screen, self.tiny_font, f"ASCOLTI {self.listen_count}/3", (205, 195, 235), (480, 500), center=True)
        if self.attack_label_timer > 0:
            draw_text(self.screen, self.small_font, "...ti sente.", (255, 237, 207), (480, 535), center=True)

    def draw_hud(self):
        # Etichetta della zona, discreta e sempre coerente con la stanza.
        names = ["STAZIONE SOMMERSA", "GIARDINO DI VETRO", "CAMERA DEL NODO"]
        pygame.draw.rect(self.screen, (6, 10, 24), (18, 17, 270, 39), border_radius=4)
        pygame.draw.rect(self.screen, (*PALETTES[self.room]["glow"], 160), (18, 17, 3, 39))
        draw_text(self.screen, self.tiny_font, "LUCE SOMMERSA", (110, 224, 231), (31, 22))
        draw_text(self.screen, self.small_font, names[self.room], (226, 230, 242), (31, 35))
        if self.room == 0:
            objective = "Segui la vibrazione" if not self.has_note else ("Parla con Pip" if not self.pip_spoken else "Raggiungi la porta a est")
        elif self.room == 1:
            objective = "Azzurro  >  Oro  >  Rosa" if not self.puzzle_done else "Attraversa la porta a est"
        else:
            objective = "Schiva. Ascolta nel silenzio." if not self.node_calm else "Raggiungi la porta in alto"
        # allineamento a destra manuale
        text_w = self.tiny_font.size(objective)[0]
        pygame.draw.rect(self.screen, (6, 10, 24), (WIDTH - text_w - 33, 17, text_w + 20, 28), border_radius=3)
        draw_text(self.screen, self.tiny_font, objective, (174, 188, 211), (WIDTH - text_w - 23, 25), shadow=False)
        if not self.battle_active:
            draw_text(self.screen, self.tiny_font, "WASD / FRECCE: MUOVITI     SHIFT: CORRI     E: INTERAGISCI     M: AUDIO", (138, 153, 180), (WIDTH // 2, HEIGHT - 20), center=True)

    def draw_interaction_prompt(self):
        if self.dialogue or self.battle_active or not self.started:
            return
        px, py = self.player
        nearby = []
        if self.room == 0:
            nearby = [("Targa", 235, 412), ("Pip", 500, 322), ("Porta", 884, 320)]
        elif self.room == 1:
            nearby = [("Nia", 160, 470), ("Specchio", 805, 478)]
        elif self.room == 2 and not self.node_awake:
            nearby = [("Segni", 480, 455)]
        choices = [(distance((px, py), (x, y)), name) for name, x, y in nearby]
        choices = [it for it in choices if it[0] < 55]
        if choices:
            name = min(choices)[1]
            pygame.draw.rect(self.screen, (8, 13, 29), (WIDTH // 2 - 118, HEIGHT - 58, 236, 25), border_radius=4)
            pygame.draw.rect(self.screen, (77, 218, 224), (WIDTH // 2 - 118, HEIGHT - 58, 3, 25))
            draw_text(self.screen, self.small_font, f"E  ·  {name}", (231, 241, 245), (WIDTH // 2, HEIGHT - 46), center=True)

    def draw_dialogue(self):
        if not self.dialogue:
            return
        speaker, text = self.dialogue[self.dialogue_index]
        box = pygame.Surface((WIDTH - 56, 145), pygame.SRCALPHA)
        pygame.draw.rect(box, (4, 8, 21, 236), (0, 0, box.get_width(), box.get_height()), border_radius=7)
        pygame.draw.rect(box, (83, 133, 157, 255), (0, 0, box.get_width(), box.get_height()), 2, border_radius=7)
        self.screen.blit(box, (28, HEIGHT - 166))
        speaker_color = (130, 237, 235) if speaker not in ("NODO", "PIP") else ((255, 138, 198) if speaker == "NODO" else (139, 244, 233))
        draw_text(self.screen, self.small_font, speaker, speaker_color, (48, HEIGHT - 153))
        shown = text[:int(self.dialogue_chars)]
        # Spezzatura manuale per tenere il testo leggibile, senza dipendere da librerie esterne.
        max_chars = 83
        words = shown.split(" ")
        lines, current = [], ""
        for word in words:
            if len(current) + len(word) + 1 > max_chars:
                lines.append(current)
                current = word
            else:
                current = (current + " " + word).strip()
        if current:
            lines.append(current)
        for i, line in enumerate(lines[:3]):
            draw_text(self.screen, self.font, line, (231, 235, 246), (48, HEIGHT - 123 + i * 24))
        if self.dialogue_chars >= len(text):
            tick = int(pygame.time.get_ticks() / 350) % 2
            if tick == 0:
                draw_text(self.screen, self.small_font, "E / Z  ▾", (143, 224, 224), (WIDTH - 115, HEIGHT - 43))

    def draw_title(self, t):
        self.screen.fill((5, 8, 24))
        # Tunnel di luci generative, come una stazione vista sott'acqua.
        for i in range(16):
            y = 110 + i * 29
            width = 90 + i * 33
            color = (14 + i, 26 + i, 49 + i)
            pygame.draw.line(self.screen, color, (WIDTH // 2 - width, y), (WIDTH // 2 + width, y), 1)
        for particle in self.particles:
            particle.draw(self.screen)
        self.glow(WIDTH // 2, 264 + math.sin(t * 1.5) * 4, (72, 222, 231), 170, 47)
        # piccola figura al centro del varco
        x, y = WIDTH // 2, 260 + math.sin(t * 2) * 4
        pygame.draw.polygon(self.screen, (23, 82, 107), [(x - 20, y + 9), (x + 20, y + 9), (x + 12, y + 42), (x, y + 49), (x - 12, y + 42)])
        pygame.draw.rect(self.screen, (182, 255, 242), (x - 13, y - 19, 26, 24))
        pygame.draw.rect(self.screen, (240, 255, 247), (x - 6, y - 27, 12, 8))
        pygame.draw.rect(self.screen, (7, 32, 48), (x - 7, y - 10, 4, 6))
        pygame.draw.rect(self.screen, (7, 32, 48), (x + 3, y - 10, 4, 6))
        draw_text(self.screen, self.big_font, "LUCE SOMMERSA", (222, 250, 248), (WIDTH // 2, 112), center=True)
        draw_text(self.screen, self.small_font, "DIECI CAPITOLI  ·  ESPLORA, ASCOLTA, RICORDA", (131, 203, 216), (WIDTH // 2, 157), center=True)
        pulse = 190 + int(50 * math.sin(t * 3))
        draw_text(self.screen, self.font, "PREMI INVIO PER INIZIARE", (pulse, 229, 226), (WIDTH // 2, 438), center=True)
        draw_text(self.screen, self.small_font, "Esplora · Ascolta · Schiva · Scegli di non colpire", (153, 167, 194), (WIDTH // 2, 480), center=True)
        draw_text(self.screen, self.tiny_font, "WASD / FRECCE muovi   E interagisci   M audio   ESC esci", (112, 134, 164), (WIDTH // 2, 559), center=True)

    def draw_ending(self, t):
        self.screen.fill((5, 9, 25))
        self.glow(WIDTH // 2, 270, (90, 227, 221), 220, 49)
        for p in self.particles:
            p.draw(self.screen)
        draw_text(self.screen, self.big_font, "FINE DEL PRIMO ECO", (213, 255, 242), (WIDTH // 2, 180), center=True)
        lines = [
            "Non hai liberato Neri: lei non era prigioniera di questo luogo.",
            "Hai liberato la parte di te rimasta sul binario, in attesa di un'altra occasione.",
            "Non puoi cambiare il saluto che non hai dato. Puoi smettere di cancellare quello che provavi.",
            "La porta si apre. Questa volta non stai fuggendo dal ricordo: lo porti con te."
        ]
        for i, line in enumerate(lines):
            draw_text(self.screen, self.font, line, (184, 203, 224), (WIDTH // 2, 263 + i * 31), center=True)
        draw_text(self.screen, self.small_font, "CAPITOLI 1–10 COMPLETATI", (113, 225, 220), (WIDTH // 2, 440), center=True)
        draw_text(self.screen, self.small_font, "INVIO: RICOMINCIA     ESC: ESCI", (125, 143, 172), (WIDTH // 2, 520), center=True)

    def draw(self, t):
        if not self.started:
            self.draw_title(t)
            pygame.display.flip()
            return
        if self.ending:
            self.draw_ending(t)
            pygame.display.flip()
            return
        if self.room >= 3:
            self.draw_extra_room(t)
            return
        self.screen.blit(self.backgrounds[self.room], (0, 0))
        palette = PALETTES[self.room]
        # Luce ambiente centrale e fari morbidi sulle uscite.
        if self.room == 0:
            self.glow(500, 320, (29, 116, 139), 190, 20)
            self.draw_door(t)
            self.draw_sign(235, 412)
            self.draw_note(t)
            self.draw_pip(500, 322, t)
            # pozze riflettenti: si muovono solo i bordi luminosi
            for i, (x, y) in enumerate(((125, 170), (830, 175), (310, 540), (595, 135))):
                r = 16 + int(2 * math.sin(t * 1.3 + i))
                pygame.draw.ellipse(self.screen, (33, 91, 108), (x - r, y - 4, r * 2, 8), 1)
        elif self.room == 1:
            self.glow(490, 315, (65, 94, 184), 220, 28)
            self.draw_door(t)
            self.draw_runes(t)
            self.draw_nia(160, 470, t)
            # Fili di vetro in alto, riflessi sottili.
            for i in range(7):
                x = 235 + i * 75
                y = 80 + int(math.sin(t + i) * 6)
                pygame.draw.line(self.screen, (49, 69, 119), (x, y), (x + 22, y + 23), 1)
        else:
            self.glow(480, 325, (115, 38, 94), 190, 22)
            self.draw_door(t)
            self.draw_boss(t)
        # Particelle, luce del giocatore e HUD.
        for particle in self.particles:
            particle.draw(self.screen)
        self.draw_player()
        self.draw_hud()
        self.draw_interaction_prompt()
        if self.battle_active:
            self.draw_arena()
        self.draw_dialogue()
        if self.hint_timer > 0 and not self.dialogue:
            alpha = int(220 * min(1, self.hint_timer * 2))
            w = self.font.size(self.hint_text)[0] + 34
            panel = pygame.Surface((w, 38), pygame.SRCALPHA)
            pygame.draw.rect(panel, (5, 10, 27, alpha), (0, 0, w, 38), border_radius=4)
            pygame.draw.rect(panel, (102, 195, 211, alpha), (0, 0, 3, 38))
            self.screen.blit(panel, (WIDTH // 2 - w // 2, 74))
            draw_text(self.screen, self.small_font, self.hint_text, (222, 235, 245), (WIDTH // 2, 93), center=True)
        if self.room_title_timer > 0:
            title = ["STAZIONE SOMMERSA", "GIARDINO DI VETRO", "CAMERA DEL NODO"][self.room]
            alpha = min(1.0, self.room_title_timer * 1.7)
            surface = self.medium_font.render(title, False, (221, 245, 248))
            surface.set_alpha(int(alpha * 230))
            rect = surface.get_rect(center=(WIDTH // 2, 94))
            self.screen.blit(surface, rect)
            line_w = int(130 * alpha)
            pygame.draw.line(self.screen, palette["glow"], (WIDTH // 2 - line_w, 114), (WIDTH // 2 + line_w, 114), 1)
        if self.flash_timer > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((148, 238, 245, int(55 * min(1, self.flash_timer / 0.2))))
            self.screen.blit(overlay, (0, 0))
        if self.battle_flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 37, 91, int(85 * self.battle_flash / 0.22)))
            self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        pygame.display.flip()

    def start_extra_chapter(self, chapter):
        data = CHAPTERS[chapter]
        self.extra_progress = 0
        self.extra_found.clear()
        self.extra_touch.clear()
        self.extra_interacted.clear()
        self.player = [float(self.player[0]), float(self.player[1])]
        self.room_title_timer = 3.0
        self.flash_timer = 0.22
        self.bullets.clear()
        self.battle_active = False
        self.audio.set_music(f"ch{chapter:02d}.ogg")
        self.particles = [Particle(self.room, True) for _ in range(75)]
        self.start_dialogue(data["intro"])

    def extra_ready_now(self):
        data = CHAPTERS[self.chapter]
        return len(self.extra_found) >= len(data["items"])

    def complete_extra_chapter(self):
        if self.chapter in self.extra_ready:
            return
        self.extra_progress = len(CHAPTERS[self.chapter]["items"])
        self.start_dialogue(CHAPTERS[self.chapter]["complete"], "extra_complete")
        self.audio.play_sfx("gate")

    def collect_extra_item(self, idx):
        data = CHAPTERS[self.chapter]
        item = data["items"][idx]
        if idx in self.extra_found:
            return
        expected = data["order"][len(self.extra_found)] if len(self.extra_found) < len(data["order"]) else idx
        if data["mode"] == "sequence" and idx != expected:
            self.audio.play_sfx("wrong")
            self.show_hint("Il ricordo non e in quest'ordine. Ascolta gli indizi e riprova.", 1.8)
            self.flash_timer = 0.08
            return
        self.extra_found.add(idx)
        self.extra_progress = len(self.extra_found)
        self.flash_timer = 0.14
        self.audio.play_sfx("pickup")
        lines = [item["line"]]
        if len(self.extra_found) == len(data["items"]):
            lines += data["complete"]
            self.start_dialogue(lines, "extra_complete")
            self.audio.play_sfx("gate")
        else:
            self.start_dialogue(lines)

    def start_extra_chapter_interact(self, idx):
        data = CHAPTERS[self.chapter]
        item = data["items"][idx]
        if idx in self.extra_found:
            self.start_dialogue([(item["line"][0], "Hai gia ascoltato questo ricordo. Ora puoi lasciarlo al suo posto.")])
            return
        self.extra_found.add(idx)
        self.extra_interacted.add(idx)
        self.extra_progress = len(self.extra_found)
        self.audio.play_sfx("pickup")
        lines = [item["line"]]
        if len(self.extra_found) == len(data["items"]):
            lines += data["complete"]
            self.start_dialogue(lines, "extra_complete")
            self.audio.play_sfx("gate")
        else:
            self.start_dialogue(lines)

    def update_extra_world(self):
        if self.dialogue or self.chapter not in CHAPTERS:
            return
        data = CHAPTERS[self.chapter]
        if data["mode"] not in ("sequence", "collect"):
            return
        for idx, item in enumerate(data["items"]):
            dist = distance(self.player, item["pos"])
            if dist > 38:
                self.extra_touch.discard(idx)
            if idx in self.extra_found:
                continue
            if dist < 29 and idx not in self.extra_touch:
                self.extra_touch.add(idx)
                self.collect_extra_item(idx)
                return

    def interact_extra(self):
        data = CHAPTERS[self.chapter]
        px, py = self.player
        candidates = []
        npc_x, npc_y = data["npc_pos"]
        candidates.append((distance((px, py), (npc_x, npc_y)), "npc", None))
        if data["mode"] == "interact":
            for idx, item in enumerate(data["items"]):
                candidates.append((distance((px, py), item["pos"]), "item", idx))
        candidates = [c for c in candidates if c[0] < 64]
        if not candidates:
            self.show_hint("Avvicinati a una persona o a un ricordo e premi E.", 1.2)
            return
        _, kind, idx = min(candidates, key=lambda c: c[0])
        if kind == "item":
            self.start_extra_chapter_interact(idx)
            return
        if self.chapter == 10:
            if not self.extra_ready_now():
                remaining = len(data["items"]) - len(self.extra_found)
                self.start_dialogue([(data["npc"], f"Mi mancano ancora {remaining} frammenti da ricordare. Non avere fretta.")])
            else:
                self.start_dialogue(data["npc_lines"], "true_ending")
            return
        if self.chapter not in self.extra_spoken:
            self.extra_spoken.add(self.chapter)
            self.start_dialogue(data["npc_lines"])
            self.audio.play_sfx("talk")
        else:
            if self.extra_ready_now():
                self.start_dialogue([(data["npc"], "Hai trovato cio che questo luogo poteva restituirti. La porta a est e aperta.")])
            else:
                collected = len(self.extra_found)
                needed = len(data["items"])
                self.start_dialogue([(data["npc"], f"Hai trovato {collected} frammenti su {needed}. Il resto non si trova stando fermi.")])

    def draw_extra_character(self, x, y, t, name, color):
        x, y = int(x), int(y + math.sin(t * 1.8 + x * 0.01) * 3)
        self.glow(x, y, color, 62, 33)
        pygame.draw.ellipse(self.screen, (4, 7, 19), (x - 19, y + 15, 38, 11))
        pygame.draw.polygon(self.screen, tuple(max(0, c - 34) for c in color), [(x - 17, y + 1), (x + 17, y + 1), (x + 12, y + 24), (x, y + 29), (x - 12, y + 24)])
        pygame.draw.polygon(self.screen, color, [(x - 11, y + 1), (x + 11, y + 1), (x + 7, y + 20), (x, y + 24), (x - 7, y + 20)])
        pygame.draw.rect(self.screen, tuple(min(255, c + 40) for c in color), (x - 10, y - 17, 20, 18))
        pygame.draw.rect(self.screen, (245, 247, 255), (x - 6, y - 22, 12, 6))
        pygame.draw.rect(self.screen, (15, 19, 33), (x - 6, y - 10, 4, 5))
        pygame.draw.rect(self.screen, (15, 19, 33), (x + 3, y - 10, 4, 5))
        if name == "IL TESTIMONE":
            pygame.draw.rect(self.screen, (255, 206, 223), (x - 2, y - 10, 4, 4))

    def draw_extra_item(self, idx, item, t):
        x, y = item["pos"]
        found = idx in self.extra_found
        palette = PALETTES[self.room]
        colors = [palette["glow"], (118, 225, 255), (255, 172, 214), (255, 218, 137)]
        color = colors[idx % len(colors)]
        if found:
            color = tuple(int(c * 0.45) for c in color)
        pulse = math.sin(t * 3 + idx * 1.6) * 3
        radius = 30 if self.chapter not in (6, 8) else 36
        self.glow(x, y, color, int(radius + pulse), 43 if not found else 13)
        if self.chapter == 6:
            pygame.draw.ellipse(self.screen, (33, 22, 49), (x - 19, y - 19, 38, 39))
            pygame.draw.ellipse(self.screen, color, (x - 19, y - 19, 38, 39), 2)
            pygame.draw.circle(self.screen, (244, 235, 255), (x - 7, y - 3), 3)
            pygame.draw.circle(self.screen, (244, 235, 255), (x + 7, y - 3), 3)
            pygame.draw.arc(self.screen, color, (x - 9, y + 2, 18, 11), 0, math.pi, 2)
        elif self.chapter == 8:
            pygame.draw.rect(self.screen, (37, 45, 58), (x - 19, y - 22, 38, 44), border_radius=3)
            pygame.draw.rect(self.screen, color, (x - 15, y - 18, 30, 36), 2)
            pygame.draw.line(self.screen, color, (x - 9, y - 7), (x + 9, y + 8), 2)
        else:
            points = [(x, y - 15 - pulse), (x + 12, y), (x, y + 15 + pulse), (x - 12, y)]
            pygame.draw.polygon(self.screen, tuple(max(0, c - 28) for c in color), points)
            pygame.draw.polygon(self.screen, color, [(x, y - 9), (x + 7, y), (x, y + 9), (x - 7, y)], 2)
            pygame.draw.circle(self.screen, (249, 250, 255), (int(x - 2), int(y - 3)), 2)
        if not found:
            label = item["name"]
            w = self.tiny_font.size(label)[0] + 14
            pygame.draw.rect(self.screen, (4, 8, 21), (int(x - w / 2), int(y + 24), w, 19), border_radius=3)
            draw_text(self.screen, self.tiny_font, label, (220, 229, 243), (x, y + 33), center=True, shadow=False)

    def draw_extra_room(self, t):
        data = CHAPTERS[self.chapter]
        palette = PALETTES[self.room]
        self.screen.blit(self.extra_maps[self.chapter], (0, 0))
        self.glow(485, 315, palette["glow"], 205, 24)
        # Segni ambientali specifici del luogo.
        if self.chapter == 2:
            for i, x in enumerate((215, 480, 760)):
                y = (205, 145, 405)[i]
                pygame.draw.line(self.screen, (61, 74, 106), (x, 50), (x, y - 22), 2)
                self.glow(x, y - 18, palette["glow"], 32, 28)
        elif self.chapter == 4:
            for i in range(8):
                x = 105 + i * 108
                pygame.draw.rect(self.screen, (46, 32, 63), (x, 65, 44, 95))
                for row in range(5):
                    pygame.draw.line(self.screen, palette["line"], (x + 6, 78 + row * 14), (x + 37, 78 + row * 14), 2)
        elif self.chapter == 5:
            pygame.draw.rect(self.screen, (24, 35, 54), (365, 85, 235, 120), border_radius=5)
            pygame.draw.rect(self.screen, palette["line"], (375, 95, 215, 100), 2, border_radius=4)
            for x in (410, 480, 550):
                pygame.draw.line(self.screen, palette["line"], (x, 95), (x, 195), 2)
        elif self.chapter == 6:
            pygame.draw.rect(self.screen, (35, 20, 41), (90, 90, 780, 90), border_radius=6)
            for x in range(120, 850, 28):
                pygame.draw.line(self.screen, (82, 37, 73), (x, 93), (x - 20, 176), 2)
            pygame.draw.line(self.screen, palette["glow"], (110, 183), (850, 183), 2)
        elif self.chapter == 7:
            pygame.draw.ellipse(self.screen, (15, 39, 56), (105, 95, 750, 450))
            pygame.draw.ellipse(self.screen, palette["line"], (105, 95, 750, 450), 2)
            for i in range(18):
                x = 130 + i * 40
                y = 310 + math.sin(t * 0.8 + i * 0.6) * 55
                pygame.draw.line(self.screen, (24, 68, 81), (x, y), (x + 20, y + 12), 1)
        elif self.chapter == 8:
            for x, y in ((110, 100), (840, 100), (110, 520), (840, 520)):
                pygame.draw.rect(self.screen, (33, 42, 52), (x - 25, y - 28, 50, 56))
                pygame.draw.rect(self.screen, palette["line"], (x - 19, y - 22, 38, 44), 2)
        elif self.chapter in (9, 10):
            for i in range(9):
                yy = 100 + i * 48
                pygame.draw.line(self.screen, palette["line"], (65, yy), (895, yy), 1)
            for x in (150, 810):
                pygame.draw.rect(self.screen, (25, 27, 46), (x - 24, 120, 48, 350))
                pygame.draw.rect(self.screen, palette["glow"], (x - 24, 120, 48, 350), 1)
        # Dettagli animati legati al luogo: riflessi d'acqua, pagine e scintille.
        if self.chapter == 7:
            for i in range(12):
                x = (i * 83 + int(t * (9 + i % 3))) % (WIDTH - 30) + 15
                y = 92 + ((i * 47 + int(math.sin(t + i) * 18)) % 450)
                pygame.draw.arc(self.screen, (37, 105, 123), (x, y, 28, 9), 0.1, math.pi - 0.1, 1)
        elif self.chapter in (4, 9):
            for i in range(7):
                x = (i * 131 + int(t * (7 + i % 2))) % (WIDTH - 24) + 12
                y = 95 + int((math.sin(t * 0.7 + i * 1.7) + 1) * 180)
                pygame.draw.polygon(self.screen, (216, 197, 223), [(x, y), (x+8, y-3), (x+12, y+7), (x+4, y+10)])
        elif self.chapter == 10:
            for i in range(13):
                x = (i * 79 + 26) % WIDTH
                y = int((t * (12 + i % 4) * (1 if i % 2 else -1) + i * 44) % HEIGHT)
                self.glow(x, y, palette["glow"], 22, 12)
        # Porta a est: una soglia che si accende soltanto al completamento del capitolo.
        gate_color = palette["glow"] if self.chapter in self.extra_ready else tuple(int(c * 0.4) for c in palette["glow"])
        self.glow(WIDTH - 22, 320, gate_color, 58, 42 if self.chapter in self.extra_ready else 14)
        pygame.draw.rect(self.screen, (4, 8, 22), (WIDTH - 39, 274, 32, 92))
        pygame.draw.rect(self.screen, gate_color, (WIDTH - 39, 274, 32, 92), 3)
        if self.chapter == 10:
            pygame.draw.rect(self.screen, (10, 16, 32), (WIDTH - 39, 274, 32, 92))
            pygame.draw.line(self.screen, palette["line"], (WIDTH - 32, 285), (WIDTH - 13, 352), 2)
        for idx, item in enumerate(data["items"]):
            self.draw_extra_item(idx, item, t)
        npc_color = (255, 202, 135) if self.chapter in (2, 5, 6) else palette["glow"]
        if self.chapter == 10:
            npc_color = (218, 242, 255) if self.extra_ready_now() else (94, 105, 139)
            # Ombra identica al protagonista, ma senza dettagli del volto.
            nx, ny = data["npc_pos"]
            self.glow(nx, ny, npc_color, 72, 42)
            pygame.draw.ellipse(self.screen, (4, 7, 18), (nx - 18, ny + 15, 36, 10))
            pygame.draw.polygon(self.screen, (35, 45, 72), [(nx - 16, ny), (nx + 16, ny), (nx + 11, ny + 25), (nx, ny + 28), (nx - 11, ny + 25)])
            pygame.draw.rect(self.screen, (15, 23, 45), (nx - 10, ny - 18, 20, 18))
            pygame.draw.rect(self.screen, npc_color, (nx - 6, ny - 10, 3, 3))
            pygame.draw.rect(self.screen, npc_color, (nx + 3, ny - 10, 3, 3))
        else:
            self.draw_extra_character(*data["npc_pos"], t, data["npc"], npc_color)
        for particle in self.particles:
            particle.draw(self.screen)
        self.draw_player()
        self.draw_extra_hud()
        self.draw_extra_interaction_prompt()
        self.draw_dialogue()
        if self.hint_timer > 0 and not self.dialogue:
            w = min(WIDTH - 50, self.font.size(self.hint_text)[0] + 34)
            panel = pygame.Surface((w, 38), pygame.SRCALPHA)
            pygame.draw.rect(panel, (5, 10, 27, 220), (0, 0, w, 38), border_radius=4)
            pygame.draw.rect(panel, (*palette["glow"], 220), (0, 0, 3, 38))
            self.screen.blit(panel, (WIDTH // 2 - w // 2, 74))
            draw_text(self.screen, self.small_font, self.hint_text, (230, 237, 246), (WIDTH // 2, 93), center=True)
        if self.room_title_timer > 0:
            alpha = min(1.0, self.room_title_timer * 1.5)
            title = self.medium_font.render(f"CAPITOLO {self.chapter}  ·  {data['title']}", False, (232, 246, 250))
            title.set_alpha(int(alpha * 235))
            rect = title.get_rect(center=(WIDTH // 2, 94))
            self.screen.blit(title, rect)
            pygame.draw.line(self.screen, palette["glow"], (WIDTH // 2 - 130, 116), (WIDTH // 2 + 130, 116), 1)
        if self.flash_timer > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((*palette["glow"], int(55 * min(1, self.flash_timer / 0.2))))
            self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.vignette, (0, 0))
        pygame.display.flip()

    def draw_extra_hud(self):
        data = CHAPTERS[self.chapter]
        palette = PALETTES[self.room]
        pygame.draw.rect(self.screen, (6, 10, 24), (18, 17, 360, 42), border_radius=4)
        pygame.draw.rect(self.screen, palette["glow"], (18, 17, 3, 42))
        draw_text(self.screen, self.tiny_font, f"LUCE SOMMERSA  /  CAPITOLO {self.chapter}", (165, 223, 228), (31, 22))
        draw_text(self.screen, self.small_font, data["title"], (226, 230, 242), (31, 37))
        objective = "Parla con la figura al centro" if self.chapter == 10 and self.extra_ready_now() else data["goal"]
        if self.chapter in self.extra_ready and self.chapter != 10:
            objective = "Il passaggio e aperto: prosegui a est."
        elif self.chapter != 10:
            objective = f"Frammenti: {len(self.extra_found)}/{len(data['items'])}  ·  {objective}"
        tw = min(WIDTH - 400, self.tiny_font.size(objective)[0])
        pygame.draw.rect(self.screen, (6, 10, 24), (WIDTH - tw - 30, 17, tw + 15, 28), border_radius=3)
        draw_text(self.screen, self.tiny_font, objective, (189, 201, 221), (WIDTH - tw - 23, 25), shadow=False)
        if not self.dialogue:
            draw_text(self.screen, self.tiny_font, "WASD / FRECCE: MUOVITI     SHIFT: CORRI     E: INTERAGISCI     M: AUDIO", (138, 153, 180), (WIDTH // 2, HEIGHT - 20), center=True)

    def draw_extra_interaction_prompt(self):
        if self.dialogue or not self.started:
            return
        data = CHAPTERS[self.chapter]
        px, py = self.player
        candidates = [(distance((px, py), data["npc_pos"]), data["npc"])]
        if data["mode"] == "interact":
            candidates += [(distance((px, py), item["pos"]), item["name"]) for item in data["items"]]
        candidates = [c for c in candidates if c[0] < 57]
        if candidates:
            name = min(candidates, key=lambda c: c[0])[1]
            pygame.draw.rect(self.screen, (8, 13, 29), (WIDTH // 2 - 140, HEIGHT - 58, 280, 25), border_radius=4)
            pygame.draw.rect(self.screen, (*PALETTES[self.room]["glow"], 210), (WIDTH // 2 - 140, HEIGHT - 58, 3, 25))
            draw_text(self.screen, self.small_font, f"E  ·  {name}", (231, 241, 245), (WIDTH // 2, HEIGHT - 46), center=True)

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.04)
            for event in pygame.event.get():
                self.handle_event(event)
            keys = pygame.key.get_pressed()
            self.update(dt, keys)
            self.draw(pygame.time.get_ticks() / 1000.0)


def main():
    try:
        Game().run()
    except KeyboardInterrupt:
        pygame.quit()


if __name__ == "__main__":
    main()
