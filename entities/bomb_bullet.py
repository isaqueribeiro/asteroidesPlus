import pygame
import math

from config import BOMB_EXPLOSION_RADIUS, BULLET_SPD, WEAPON_COLOR
from entities.bullet import Bullet


class BombBullet(Bullet):
    """Projétil lento que causa explosão em área ao atingir um asteroide."""
    EXPLOSION_RADIUS = BOMB_EXPLOSION_RADIUS

    def __init__(self, x: float, y: float, angle: float):
        color = WEAPON_COLOR['BOMBA']
        super().__init__(x, y, angle, color, speed=BULLET_SPD, size=6)
        self._pulse = 0.0

    def update(self):
        super().update()
        if self.alive():
            # Pulsa a cor para se destacar
            self._pulse = (self._pulse + 0.15) % (2 * math.pi)
            bright = int(180 + 75 * math.sin(self._pulse))
            dim = max(0, bright - 60)
            col = (bright, dim, 0)
            d = self.radius*2 + 2
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, col, (d//2, d//2), self.radius)

    def alive(self) -> bool:
        return bool(self.groups())
