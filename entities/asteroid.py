import pygame
import math
import random

from typing import List

from config import AST_INFO, WIDTH, HEIGHT, CYAN, WHITE
from utils.math_utils import ang_vec, wrap


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, size: str, x: float = None, y: float = None, speed_mul: float = 1.0):
        super().__init__()
        info = AST_INFO[size]
        self.size       = size
        self.radius     = info['radius']
        self.pts_value  = info['pts']
        self.child_size = info['child']
        self.nkids      = info['nkids']

        if x is None: x, y = self._edge_pos()
        self.x, self.y = float(x), float(y)

        spd = random.uniform(info['spd_min'], info['spd_max']) * speed_mul
        self.vx, self.vy = ang_vec(random.uniform(0, 360), spd)
        self.rot     = random.uniform(0, 360)
        self.rot_spd = random.uniform(-1.8, 1.8)
        self._verts  = self._make_verts()

        dim = (self.radius + 4) * 2
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(self.x), int(self.y)))
        self._render()

    def _edge_pos(self):
        side = random.randint(0, 3); r = self.radius + 5
        if side == 0: return random.uniform(0, WIDTH), -r
        if side == 1: return WIDTH+r, random.uniform(0, HEIGHT)
        if side == 2: return random.uniform(0, WIDTH), HEIGHT+r
        return -r, random.uniform(0, HEIGHT)

    def _make_verts(self):
        n = random.randint(8, 12)
        return [(360.0/n*i, self.radius*random.uniform(0.72, 1.0)) for i in range(n)]

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = cy = self.image.get_width() // 2
        pts = [(cx + math.cos(math.radians(a+self.rot))*r,
                cy + math.sin(math.radians(a+self.rot))*r)
               for a, r in self._verts]
        col = {'large': CYAN, 'medium': (160, 210, 255), 'small': WHITE}[self.size]
        if len(pts) >= 3:
            pygame.draw.polygon(self.image, col, pts, 2)

    def update(self):
        self.x, self.y = wrap(self.x+self.vx, self.y+self.vy)
        self.rot = (self.rot+self.rot_spd) % 360
        self._render()
        self.rect.center = (int(self.x), int(self.y))

    def split(self, speed_mul: float = 1.0) -> List['Asteroid']:
        if not self.child_size: return []
        return [Asteroid(self.child_size, self.x, self.y, speed_mul*1.15)
                for _ in range(self.nkids)]
