from typing import Sequence
import numpy as np

from game.entities.bullet import Bullet
from game.entities.bullets import Bullets
from game.game_field import GameField
from game.systems.object_protocol import DamageableObject


class Damage:

    def __init__(
        self,
        damageables: Sequence[DamageableObject],
        bullets: Bullets,
        game_field: GameField,
    ):
        self.__bullets = bullets
        self.__damageables = damageables
        self.__game_field = game_field

    def update(self, dt: float):
        for bullet in self.__bullets:
            if bullet.is_destroyed() == True:
                self.__destroy(bullet)
            bullet.update(dt)

        for bullet in self.__bullets:
            for player in self.__damageables:
                if bullet.rect.colliderect(player.rect):
                    is_dead = player.damage(bullet)

                    for p in self.__damageables:
                        if p._color == bullet._color and player._color != bullet._color and is_dead == "kill":  # type: ignore
                            p.add_score()  # type: ignore
                            self.__destroy(bullet)
                            return

                        self.__destroy(bullet)
            for (bx, by), block in np.ndenumerate(self.__game_field.field):
                if block is not None:
                    block_rect = self.__game_field._get_block_rect(bx, by)
                    if bullet.rect.colliderect(block_rect):
                        self.__destroy(bullet)
                        break

    def __destroy(self, bullet: Bullet):
        if bullet in self.__bullets:
            self.__bullets.remove(bullet)
