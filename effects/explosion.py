import pygame

from config import BOMB_EXPLOSION_RADIUS, WEAPON_COLOR


class BombExplosion:
    """Anel de onda de choque que se expande após impacto da bomba."""
    RADIUS = BOMB_EXPLOSION_RADIUS

    def __init__(self, x: float, y: float):
        self.x, self.y = x, y
        self.t = 0.0        # progresso 0→1

    def update(self, dt: float) -> bool:
        self.t += dt * 2.8
        return self.t < 1.0

    def draw(self, surf: pygame.Surface):
        r = int(self.RADIUS * self.t)
        if r <= 0: return
        fade = 1.0 - self.t
        col  = WEAPON_COLOR['BOMBA']
        c1   = tuple(int(v * fade)       for v in col)
        c2   = tuple(int(v * fade * 0.4) for v in col)
        pygame.draw.circle(surf, c1, (int(self.x), int(self.y)), r, 3)
        if r > 10:
            pygame.draw.circle(surf, c2, (int(self.x), int(self.y)), max(1, r-10), 1)
