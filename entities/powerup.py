import pygame
import math
import random

from typing import Optional

from config import PU_LIFETIME, PU_SPEED, WEAPON_COLOR, WHITE
from utils.math_utils import ang_vec, wrap


class PowerUp(pygame.sprite.Sprite):
    LIFETIME = PU_LIFETIME
    radius   = 14
    _font: Optional[pygame.font.Font] = None

    _LETTER = {
        'BOMBA': 'BM', 'TRIPLO': 'D3', 'LASER': 'LS',
        'ESPALHADO': 'S5', 'TRASEIRO': 'TR',
    }

    SPEED = PU_SPEED

    def __init__(self, weapon: str, x: float, y: float):
        super().__init__()
        self.weapon = weapon
        self.x, self.y = float(x), float(y)
        self.life = self.LIFETIME
        self.rot  = random.uniform(0, 360)
        self.vx, self.vy = ang_vec(random.uniform(0, 360), self.SPEED)
        dim = 34
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(x), int(y)))
        self._render()

    @classmethod
    def _get_font(cls) -> pygame.font.Font:
        if cls._font is None:
            cls._font = pygame.font.SysFont("Courier New", 11, bold=True)
        return cls._font

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        if self.life < 4.0 and int(self.life * 6) % 2 == 1:
            return
        cx = cy = self.image.get_width() // 2
        col = WEAPON_COLOR[self.weapon]
        r = 13
        pts = [(cx + math.cos(math.radians(self.rot + 45 + 90*i)) * r,
                cy + math.sin(math.radians(self.rot + 45 + 90*i)) * r)
               for i in range(4)]
        dark = tuple(int(c * 0.20) for c in col)
        pygame.draw.polygon(self.image, dark, pts, 0)
        pygame.draw.polygon(self.image, col,  pts, 2)
        pygame.draw.circle(self.image, col, (cx, cy), 3)
        lbl = self._get_font().render(self._LETTER[self.weapon], True, WHITE)
        self.image.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    def update(self, dt: float):
        self.life -= dt
        if self.life <= 0:
            self.kill(); return
        self.x, self.y = wrap(self.x + self.vx, self.y + self.vy)
        self.rot = (self.rot + 2.2) % 360
        self._render()
        self.rect.center = (int(self.x), int(self.y))
