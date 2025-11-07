import ctypes


def get_screen_resolution() -> tuple[float, float]:
    ctypes.windll.user32.SetProcessDPIAware()
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    return width, height


CURRENT_SCREEN_SIZE = get_screen_resolution()
GAME_FIELD_PROPORTIONS = float(16 / 9)

SCREEN_WIDTH = CURRENT_SCREEN_SIZE[0] * 0.8
SCREEN_HEIGHT = SCREEN_WIDTH / GAME_FIELD_PROPORTIONS

GAME_FIELD_WIDTH = SCREEN_WIDTH
GAME_FIELD_HEIGHT = GAME_FIELD_WIDTH / GAME_FIELD_PROPORTIONS


# Game consts
FPS = 120

BLOCK_SIZE = GAME_FIELD_WIDTH / 41

PLAYER_SPEED = BLOCK_SIZE / 5.5
PLAYER_JUMP_FORCE = BLOCK_SIZE / 4
PLAYER_HEALTH = 100

BULLET_WIDTH = BLOCK_SIZE / 2
BULLET_HEIGHT = BLOCK_SIZE / 3
BULLET_SPEED = BLOCK_SIZE / 3.0
BULLET_DAMAGE = 10

ENEMY_SPEED = 1.7

MAX_ANTI_GRAVITY = BLOCK_SIZE / 700
CHANGE_ANTI_GRAVITY = 0.03

GRAVITY = BLOCK_SIZE / 115

IS_DEBUG = False


# Colors
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
WHITE = (1, 1, 1)
ORANGE = (1, 0.5, 0)
YELLOW = (1, 1, 0)
DARK_GREY = (0.2, 0.2, 0.2)
GREY = (0.25, 0.25, 0.25)
