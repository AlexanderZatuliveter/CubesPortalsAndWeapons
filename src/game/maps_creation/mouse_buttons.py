import pygame
from game.consts import GAME_FIELD_WIDTH
from game.game_field import GameField


class Mouse:
    def __init__(self):
        self.blocks = []

    def update(self, game_field: GameField, screen: pygame.Surface):
        left, middle, right = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        scale = screen.get_width() / pygame.display.get_window_size()[0]
        mouse_x, mouse_y = int(mouse_x * scale), int(mouse_y * scale)

        if left:
            game_field.put_block_by_screen_pos(mouse_x, mouse_y)
            game_field.put_block_by_screen_pos(int(GAME_FIELD_WIDTH) - mouse_x, mouse_y)
        if right:
            game_field.hit_block_by_screen_pos(mouse_x, mouse_y)
            game_field.hit_block_by_screen_pos(int(GAME_FIELD_WIDTH) - mouse_x, mouse_y)
