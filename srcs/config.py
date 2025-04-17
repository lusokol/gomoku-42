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
