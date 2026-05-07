import pygame
import random

from typing import Tuple
from utils.math_utils import ang_vec


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size')

    def __init__(self, x: float, y: float, color: Tuple):
        spd = random.uniform(1.5, 6.0)
        self.vx, self.vy = ang_vec(random.uniform(0, 360), spd)
        self.x, self.y = x, y
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.color = color
        self.size = random.uniform(1.5, 3.5)

    def update(self) -> bool:
        self.life -= 1
        if self.life <= 0: return False
        self.x += self.vx; self.vx *= 0.95
        self.y += self.vy; self.vy *= 0.95
        return True

    def draw(self, surf: pygame.Surface):
        t = self.life / self.max_life
        col = tuple(int(c * t) for c in self.color)
        r = max(1, int(self.size * (0.4 + 0.6*t) + 0.5))
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), r)
