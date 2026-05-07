import pygame
import math
import random

from config import HUNTER_BASE_SPEED, HUNTER_SPEED_INC, HUNTER_PTS_BASE, HUNTER_LIFETIME, WIDTH, HUNTER_TURN_SPEED, \
    HEIGHT, ORANGE, RED, WHITE
from effects.particle import Particle
from utils.math_utils import ang_vec, wrap


class HunterShip:
    """Nave inimiga que persegue o jogador ao final de cada level."""
    radius = 16

    def __init__(self, level: int):
        self.speed = HUNTER_BASE_SPEED + (level - 1) * HUNTER_SPEED_INC
        self.pts   = HUNTER_PTS_BASE * level
        self.life  = HUNTER_LIFETIME

        side = random.randint(0, 3); r = self.radius + 12
        if   side == 0: self.x, self.y = random.uniform(0, WIDTH),  -r
        elif side == 1: self.x, self.y = WIDTH + r, random.uniform(0, HEIGHT)
        elif side == 2: self.x, self.y = random.uniform(0, WIDTH),  HEIGHT + r
        else:           self.x, self.y = -r, random.uniform(0, HEIGHT)

        dx = WIDTH//2 - self.x; dy = HEIGHT//2 - self.y
        self.angle = math.degrees(math.atan2(-dy, dx))
        self._pulse = 0.0

    def update(self, px: float, py: float, dt: float, parts: list) -> bool:
        self.life -= dt
        if self.life <= 0:
            return False

        # Steering: girar gradualmente em direção ao jogador
        dx, dy = px - self.x, py - self.y
        target = math.degrees(math.atan2(-dy, dx))
        diff   = (target - self.angle + 180) % 360 - 180
        self.angle += max(-HUNTER_TURN_SPEED, min(HUNTER_TURN_SPEED, diff))

        vx, vy = ang_vec(self.angle, self.speed)
        self.x, self.y = wrap(self.x + vx, self.y + vy)

        self._pulse = (self._pulse + dt * 10) % (2 * math.pi)

        # Rastro de motor
        if random.random() < 0.55:
            tx = self.x - ang_vec(self.angle, 20)[0]
            ty = self.y - ang_vec(self.angle, 20)[1]
            p  = Particle(tx, ty, ORANGE)
            p.vx *= 0.25; p.vy *= 0.25
            parts.append(p)

        return True

    def draw(self, surf: pygame.Surface):
        a = self.angle; N = 20
        pulse = 0.65 + 0.35 * math.sin(self._pulse)
        fill  = (int(255 * pulse), int(30 * pulse), int(30 * pulse))
        pts = [
            (self.x + math.cos(math.radians(a))      * N,
             self.y - math.sin(math.radians(a))      * N),
            (self.x + math.cos(math.radians(a - 138)) * N * 0.78,
             self.y - math.sin(math.radians(a - 138)) * N * 0.78),
            (self.x + math.cos(math.radians(a + 180)) * N * 0.32,
             self.y - math.sin(math.radians(a + 180)) * N * 0.32),
            (self.x + math.cos(math.radians(a + 138)) * N * 0.78,
             self.y - math.sin(math.radians(a + 138)) * N * 0.78),
        ]
        pygame.draw.polygon(surf, fill, pts, 0)
        pygame.draw.polygon(surf, RED,  pts, 2)
        # Mira central
        ix, iy = int(self.x), int(self.y)
        pygame.draw.line(surf, WHITE, (ix - 5, iy), (ix + 5, iy), 1)
        pygame.draw.line(surf, WHITE, (ix, iy - 5), (ix, iy + 5), 1)
