import pygame

from config import RED, BULLET_SPD, BULLET_LIFE, WIDTH, HEIGHT
from utils.math_utils import ang_vec


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle: float,
                 color=RED, speed: float = BULLET_SPD, size: int = 3):
        super().__init__()
        self.radius = size
        self.x, self.y = x, y
        self.vx, self.vy = ang_vec(angle, speed)
        self.life = BULLET_LIFE
        dim = size*2 + 2
        self.image = pygame.Surface((dim, dim), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (dim//2, dim//2), size)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self):
        self.life -= 1
        if self.life <= 0 or not (-12 <= self.x <= WIDTH+12 and -12 <= self.y <= HEIGHT+12):
            self.kill(); return
        self.x += self.vx; self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
