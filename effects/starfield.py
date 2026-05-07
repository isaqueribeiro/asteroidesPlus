import pygame
import random

from config import WIDTH, HEIGHT


class StarField:
    def __init__(self, n: int = 130):
        self._stars = [
            (random.randint(0, WIDTH), random.randint(0, HEIGHT), random.choice([1, 1, 2]))
            for _ in range(n)
        ]

    def draw(self, surf: pygame.Surface):
        for x, y, r in self._stars:
            b = random.randint(120, 200)
            pygame.draw.circle(surf, (b, b, b), (x, y), r)
