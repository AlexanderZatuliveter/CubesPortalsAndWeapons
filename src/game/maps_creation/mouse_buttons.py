import pygame
from game.game_field import GameField


class Mouse:
    def __init__(self):
        self.blocks = []

    def update(self, game_field: GameField):
        left, middle, right = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if left:
            game_field.put_block_by_screen_pos(mouse_x, mouse_y)
        if right:
            game_field.hit_block_by_screen_pos(mouse_x, mouse_y)
