import time

from typing import Tuple

from config import EXTRA_LIFE_PTS, STREAK_NEEDED, STREAK_BONUS, MENU, START_LIVES, PLAYING, MAX_LIVES, GAME_OVER, \
    DIFF_AST_STEP, DIFF_AST_MAX, DIFF_SPEED_STEP, DIFF_SPEED_MAX, DIFF_SPAWN_START, DIFF_SPAWN_MIN, DIFF_SPAWN_STEP, \
    DIFF_SPAWN_DEC


class GameManager:
    EXTRA_LIFE = EXTRA_LIFE_PTS
    STREAK_N   = STREAK_NEEDED
    STREAK_PTS = STREAK_BONUS

    def __init__(self):
        self.state = MENU
        self._reset()

    def _reset(self):
        self.score        = 0
        self.lives        = START_LIVES
        self.streak       = 0
        self.next_life_at = self.EXTRA_LIFE
        self.start_time   = 0.0
        self.elapsed      = 0.0
        self.spawn_acc    = 0.0

    def start(self):
        self._reset()
        self.start_time = time.time()
        self.state      = PLAYING

    def tick(self):
        if self.state == PLAYING:
            self.elapsed = time.time() - self.start_time

    def add_score(self, pts: int) -> Tuple[bool, bool]:
        self.score  += pts; self.streak += 1
        streak_bonus = False
        if self.streak >= self.STREAK_N:
            self.score += self.STREAK_PTS; self.streak = 0; streak_bonus = True
        got_life = False
        if self.lives < MAX_LIVES and self.score >= self.next_life_at:
            self.lives += 1; self.next_life_at += self.EXTRA_LIFE; got_life = True
        return got_life, streak_bonus

    def lose_life(self) -> bool:
        self.streak  = 0; self.lives -= 1
        if self.lives <= 0:
            self.elapsed = time.time() - self.start_time
            self.state   = GAME_OVER; return True
        return False

    @property
    def target_asteroids(self) -> int:
        return min(3 + self.score // DIFF_AST_STEP, DIFF_AST_MAX)

    @property
    def speed_mul(self) -> float:
        return min(1.0 + (self.score // DIFF_SPEED_STEP) * 0.25, DIFF_SPEED_MAX)

    @property
    def spawn_interval(self) -> float:
        return max(DIFF_SPAWN_START - (self.score // DIFF_SPAWN_STEP) * DIFF_SPAWN_DEC,
                   DIFF_SPAWN_MIN)

    def should_spawn(self, dt: float, current: int) -> bool:
        if current >= self.target_asteroids:
            self.spawn_acc = 0.0; return False
        self.spawn_acc += dt
        if self.spawn_acc >= self.spawn_interval:
            self.spawn_acc = 0.0; return True
        return False

    @property
    def level(self) -> int:
        return self.score//5000 + 1
