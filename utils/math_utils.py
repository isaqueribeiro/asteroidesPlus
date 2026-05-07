import math
from typing import Tuple
from config import WIDTH, HEIGHT


def wrap(x: float, y: float) -> Tuple[float, float]:
    return x % WIDTH, y % HEIGHT

def ang_vec(deg, mag=1):
    r = math.radians(deg)
    return math.cos(r) * mag, -math.sin(r) * mag

def ray_circle(px: float, py: float, dx: float, dy: float,
               cx: float, cy: float, r: float) -> Tuple[bool, float]:
    """Interseção raio→círculo. Retorna (acertou, distância t)."""
    fx, fy = px - cx, py - cy
    a = dx*dx + dy*dy
    b = 2*(fx*dx + fy*dy)
    c = fx*fx + fy*fy - r*r
    disc = b*b - 4*a*c
    if disc < 0:
        return False, -1.0
    sd = math.sqrt(disc)
    t1 = (-b - sd) / (2*a)
    t2 = (-b + sd) / (2*a)
    if t1 >= 0: return True, t1
    if t2 >= 0: return True, t2
    return False, -1.0

