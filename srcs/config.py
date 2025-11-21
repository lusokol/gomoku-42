from soundManager import SoundManager

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
HPC = SCREEN_HEIGHT / 100
WPC = SCREEN_WIDTH // 3 / 100

GRID_SIZE = 19
STONE_WHITE = (230, 230, 230)
STONE_BLACK = (43, 43, 43)

COLOR_MENU = (115, 61, 0, 200)
COLOR_BUTTON = (64, 31, 1)
COLOR_BUTTON_HOVER = (105, 52, 2)

NOTIFICATION = {"message": None, "start_time": None, "duration": 2}  # secondes

SOUND_VOLUME = 5 # [0:10]
MUSIC_VOLUME = 5 # [0:10]
sound_manager = SoundManager()

# codes des differents coups avec leur score attribué

# JX-

codes = {
    # Value from 0 to CENTER about how center is you piece
    "CENTER": 50,  # Réduit car moins important que les menaces

    # === IA (J1) – Alignements ===
    "J1_5": 10000000,  # Victoire immédiate
    "J1_4_OPEN": 100000,  # Menace de victoire critique (gagne au prochain coup)
    "J1_4_SEMI": 15000,  # Menace forte mais bloquable d'un côté
    "J1_4_CLOSED": 3000,  # Moins prioritaire
    "J1_3_OPEN": 12000,  # Peut devenir 4_OPEN ou créer un fork
    "J1_3_SEMI": 3000,  # Développement intéressant
    "J1_3_CLOSED": 800,  # Peu utile
    "J1_2_OPEN": 800,  # Début de développement
    "J1_2_SEMI": 300,
    "J1_2_CLOSED": 100,
    "J1_1": 20,

    # === IA (J1) – Blocages sur J2 ===
    "J1_BLOCK_5": 10000000,  # Bloquer une victoire
    "J1_BLOCK_4_OPEN": 90000,  # CRITIQUE : bloquer 4 ouverts adverses
    "J1_BLOCK_4_SEMI": 18000,  # Très important
    "J1_BLOCK_4_CLOSED": 18000,
    "J1_BLOCK_3_OPEN": 10000,  # Important car peut devenir dangereux
    "J1_BLOCK_3_SEMI": 6000,
    "J1_BLOCK_3_CLOSED": 800,
    "J1_BLOCK_2_OPEN": 400,
    "J1_BLOCK_2_SEMI": 250,
    "J1_BLOCK_2_CLOSED": 80,
    "J1_BLOCK_1": 30,

    # === IA (J1) – Captures ===
    "J1_C": [200, 1000, 5000, 20000, 10000000],  # Progression agressive

    # === Joueur (J2) – Alignements ===
    "J2_5": 10000000,
    "J2_4_OPEN": 100000,
    "J2_4_SEMI": 15000,
    "J2_4_CLOSED": 3000,
    "J2_3_OPEN": 12000,
    "J2_3_SEMI": 3000,
    "J2_3_CLOSED": 800,
    "J2_2_OPEN": 800,
    "J2_2_SEMI": 300,
    "J2_2_CLOSED": 100,
    "J2_1": 20,

    # === Joueur (J2) – Blocages sur J1 ===
    "J2_BLOCK_5": 10000000,
    "J2_BLOCK_4_OPEN": 90000,
    "J2_BLOCK_4_SEMI": 18000,
    "J2_BLOCK_4_CLOSED": 18000,
    "J2_BLOCK_3_OPEN": 10000,
    "J2_BLOCK_3_SEMI": 6000,
    "J2_BLOCK_3_CLOSED": 800,
    "J2_BLOCK_2_OPEN": 400,
    "J2_BLOCK_2_SEMI": 250,
    "J2_BLOCK_2_CLOSED": 80,
    "J2_BLOCK_1": 30,

    # === Joueur (J2) – Captures ===
    "J2_C": [200, 1000, 5000, 20000, 10000000]
}
