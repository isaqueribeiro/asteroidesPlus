import pygame
import math
import random

from typing import List

from config import WIDTH, HEIGHT, INVINCIBLE, WEAPON_COLOR, YELLOW, GREEN, WHITE, ORANGE, ROT_SPEED, ACCEL, MAX_SPEED, \
    FRICTION, WEAPON_CD, RED, WEAPON_DURATION
from entities.bomb_bullet import BombBullet
from entities.bullet import Bullet
from utils.math_utils import ang_vec, wrap


class Player(pygame.sprite.Sprite):
    NOSE   = 22
    radius = 15

    def __init__(self):
        super().__init__()
        self.x, self.y   = float(WIDTH//2), float(HEIGHT//2)
        self.angle        = 90.0
        self.vx = self.vy = 0.0
        self.invincible   = INVINCIBLE
        self.shoot_cd     = 0
        self.thrusting    = False
        self.weapon       = 'NORMAL'
        self.weapon_timer = 0.0

        dim = self.NOSE * 3
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=(int(self.x), int(self.y)))
        self._render()

    def _pts(self, cx, cy):
        N, a = self.NOSE, self.angle
        return [
            (cx + math.cos(math.radians(a))       * N,
             cy - math.sin(math.radians(a))       * N),
            (cx + math.cos(math.radians(a-135))   * N * 0.85,
             cy - math.sin(math.radians(a-135))   * N * 0.85),
            (cx + math.cos(math.radians(a+180))   * N * 0.38,
             cy - math.sin(math.radians(a+180))   * N * 0.38),
            (cx + math.cos(math.radians(a+135))   * N * 0.85,
             cy - math.sin(math.radians(a+135))   * N * 0.85),
        ]

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        if self.invincible > 0 and int(self.invincible*8) % 2 == 1:
            return
        cx = cy = self.image.get_width() // 2
        pts = self._pts(cx, cy)
        col = (WEAPON_COLOR[self.weapon] if self.weapon != 'NORMAL'
               else (YELLOW if self.invincible > 0 else GREEN))
        pygame.draw.polygon(self.image, col, pts, 0)
        pygame.draw.polygon(self.image, WHITE, pts, 1)
        if self.thrusting:
            N, a = self.NOSE, self.angle
            flame = [
                (cx + math.cos(math.radians(a-150))*N*0.55,
                 cy - math.sin(math.radians(a-150))*N*0.55),
                (cx + math.cos(math.radians(a+180))*N*random.uniform(0.55,1.05),
                 cy - math.sin(math.radians(a+180))*N*random.uniform(0.55,1.05)),
                (cx + math.cos(math.radians(a+150))*N*0.55,
                 cy - math.sin(math.radians(a+150))*N*0.55),
            ]
            pygame.draw.polygon(self.image, ORANGE, flame, 0)

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float):
        if self.shoot_cd  > 0: self.shoot_cd  -= 1
        if self.invincible > 0: self.invincible -= dt
        if self.weapon_timer > 0:
            self.weapon_timer -= dt
            if self.weapon_timer <= 0:
                self.weapon_timer = 0.0
                self.weapon = 'NORMAL'

        if keys[pygame.K_LEFT]:  self.angle += ROT_SPEED
        if keys[pygame.K_RIGHT]: self.angle -= ROT_SPEED

        self.thrusting = bool(keys[pygame.K_UP])
        if self.thrusting:
            ax, ay = ang_vec(self.angle, ACCEL)
            self.vx += ax; self.vy += ay
            spd = math.hypot(self.vx, self.vy)
            if spd > MAX_SPEED:
                self.vx = self.vx/spd*MAX_SPEED
                self.vy = self.vy/spd*MAX_SPEED

        self.vx *= FRICTION; self.vy *= FRICTION
        self.x, self.y = wrap(self.x+self.vx, self.y+self.vy)
        self._render()
        self.rect.center = (int(self.x), int(self.y))

    def try_shoot(self) -> List[Bullet]:
        """Retorna lista de bullets. LASER retorna [] (tratado pelo Game)."""
        if self.shoot_cd > 0 or self.weapon == 'LASER':
            return []
        self.shoot_cd = WEAPON_CD[self.weapon]
        col = WEAPON_COLOR[self.weapon]
        N   = self.NOSE + 5
        bx  = self.x + ang_vec(self.angle, N)[0]
        by  = self.y + ang_vec(self.angle, N)[1]
        a   = self.angle

        if self.weapon == 'BOMBA':
            return [BombBullet(bx, by, a)]

        if self.weapon == 'TRIPLO':
            return [Bullet(bx, by, a+off, col) for off in (-22, 0, 22)]

        if self.weapon == 'ESPALHADO':
            return [Bullet(bx, by, a+off, col, speed=8.5, size=2)
                    for off in (-44, -22, 0, 22, 44)]

        if self.weapon == 'TRASEIRO':
            bx2 = self.x + ang_vec(a+180, N)[0]
            by2 = self.y + ang_vec(a+180, N)[1]
            return [Bullet(bx, by, a, col), Bullet(bx2, by2, a+180, col)]

        # NORMAL
        return [Bullet(bx, by, a, RED)]

    def collect_weapon(self, weapon: str):
        self.weapon       = weapon
        self.weapon_timer = WEAPON_DURATION

    def respawn(self):
        self.x, self.y    = float(WIDTH//2), float(HEIGHT//2)
        self.vx = self.vy = 0.0
        self.invincible   = INVINCIBLE
        self.weapon       = 'NORMAL'
        self.weapon_timer = 0.0

    @property
    def is_invincible(self) -> bool:
        return self.invincible > 0
