import pygame

pygame.init()

START_SCREEN_WIDTH = int(pygame.display.Info().current_w * 0.8)
START_SCREEN_HEIGHT = int(pygame.display.Info().current_h * 0.8)

GAME_FIELD_WIDTH = START_SCREEN_WIDTH
GAME_FIELD_HEIGHT = START_SCREEN_HEIGHT
GAME_FIELD_PROPORTIONS = 16 / 9

PLAYER_SPEED = 15
PLAYER_JUMP_FORCE = 20

GRAVITY = 1.0
