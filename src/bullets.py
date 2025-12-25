from bullet import Bullet


class Bullets(list[Bullet]):
    def draw(self):
        for bullet in self:
            bullet.draw()

    def add_bullet(self, bullet: Bullet):
        self.append(bullet)

    def clear_by_color(self, color: tuple[float, float, float]):
        self = [b for b in self if b._color != color]
