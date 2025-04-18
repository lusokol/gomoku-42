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

sound_manager = SoundManager()

# codes des differents coups avec leur score attribué

# JX-

codes = {
    # === IA (J1) – Alignements ===
    "J1_5": 999999,
    "J1_4_OPEN": 9000,
    "J1_4_SEMI": 6000,
    "J1_4_CLOSED": 2000,
    "J1_3_OPEN": 4000,
    "J1_3_SEMI": 2000,
    "J1_3_CLOSED": 500,
    "J1_2_OPEN": 500,
    "J1_2_SEMI": 200,
    "J1_2_CLOSED": 50,
    "J1_1": 10,

    # === IA (J1) – Blocages sur J2 ===
    "J1_BLOCK_4_SEMI": 6000,
    "J1_BLOCK_4_CLOSED": 9000,
    "J1_BLOCK_3_SEMI": 3000,
    "J1_BLOCK_3_CLOSED": 500,
    "J1_BLOCK_2_SEMI": 200,
    "J1_BLOCK_2_CLOSED": 50,
    "J1_BLOCK_1": 10,

    # === IA (J1) – Captures ===
    "J1_C": [150, 500, 2000, 6000, 999999],  # Indexé par nombre de captures faites

    # === Joueur (J2) – Alignements ===
    "J2_5": 999999,
    "J2_4_OPEN": 9000,
    "J2_4_SEMI": 6000,
    "J2_4_CLOSED": 2000,
    "J2_3_OPEN": 4000,
    "J2_3_SEMI": 2000,
    "J2_3_CLOSED": 500,
    "J2_2_OPEN": 500,
    "J2_2_SEMI": 200,
    "J2_2_CLOSED": 50,
    "J2_1": 10,

    # === Joueur (J2) – Blocages sur J1 ===
    "J2_BLOCK_5": 999999,
    "J2_BLOCK_4_OPEN": 9000,
    "J2_BLOCK_4_SEMI": 6000,
    "J2_BLOCK_4_CLOSED": 2000,
    "J2_BLOCK_3_OPEN": 4000,
    "J2_BLOCK_3_SEMI": 2000,
    "J2_BLOCK_3_CLOSED": 500,
    "J2_BLOCK_2_OPEN": 500,
    "J2_BLOCK_2_SEMI": 200,
    "J2_BLOCK_2_CLOSED": 50,
    "J2_BLOCK_1": 10,

    # === Joueur (J2) – Captures ===
    "J2_C": [150, 500, 2000, 6000, 999999]  # Indexé par nombre de captures faites
}
