import sys

import pygame
import math
import random
import time

from typing import List, Optional, Tuple

from config import *
from core.game_manager import GameManager
from core.sound_manager import SoundManager
from effects.explosion import BombExplosion
from effects.particle import Particle
from effects.starfield import StarField
from entities.asteroid import Asteroid
from entities.bomb_bullet import BombBullet
from entities.hunter_ship import HunterShip
from entities.player import Player
from entities.powerup import PowerUp
from utils.math_utils import ray_circle, ang_vec


def explode(parts: list, x: float, y: float, n: int = 14, color=WHITE):
    for _ in range(n):
        parts.append(Particle(x, y, color))

class Game:
    _PU_SPAWN_MIN    = PU_SPAWN_MIN
    _PU_SPAWN_MAX    = PU_SPAWN_MAX
    _PU_MAX_ON_SCREEN = PU_MAX_ON_SCREEN

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 1024)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(GAME_NAME)
        self.clock  = pygame.time.Clock()

        fn = "Courier New"
        self.f_lg = pygame.font.SysFont(fn, 52, bold=True)
        self.f_md = pygame.font.SysFont(fn, 28, bold=True)
        self.f_sm = pygame.font.SysFont(fn, 19)
        self.f_xs = pygame.font.SysFont(fn, 14)

        self.stars = StarField(130)
        self.gm    = GameManager()
        self.snd   = SoundManager()
        self.snd.start_music()

        self._sprites  = pygame.sprite.Group()
        self._asts     = pygame.sprite.Group()
        self._bullets  = pygame.sprite.Group()
        self._powerups = pygame.sprite.Group()
        self._parts: List[Particle]      = []
        self._bomb_waves: List[BombExplosion] = []
        self._player: Optional[Player]  = None

        # Estado do laser contínuo
        self._laser_active = False
        self._laser_end: Optional[Tuple[float, float]] = None
        self._laser_cd  = 0.0   # cooldown de dano

        # Estado do caçador
        self._hunter: Optional[HunterShip] = None
        self._prev_level  = 1
        self._hunter_warn = 0.0   # segundos restantes do aviso

        self._pu_timer = self._PU_SPAWN_MIN

        self._menu_asts = pygame.sprite.Group()
        for _ in range(5):
            a = Asteroid('large')
            a.x = random.uniform(0, WIDTH)
            a.y = random.uniform(0, HEIGHT)
            self._menu_asts.add(a)

        self._flash_msg = ""
        self._flash_col = WHITE
        self._flash_t   = 0.0

    # ─── inicialização ────────────────────────────────────────────────────────
    def _new_game(self):
        self._sprites.empty(); self._asts.empty()
        self._bullets.empty(); self._powerups.empty()
        self._parts.clear();   self._bomb_waves.clear()
        self._laser_active = False; self._laser_end = None; self._laser_cd = 0.0
        self._hunter = None; self._prev_level = 1; self._hunter_warn = 0.0
        self.snd.stop_hunter_alert()
        self.gm.start()
        self._pu_timer = random.uniform(self._PU_SPAWN_MIN, self._PU_SPAWN_MAX)

        self._player = Player()
        self._sprites.add(self._player)
        for _ in range(3): self._spawn_ast()

    def _spawn_ast(self, x=None, y=None):
        a = Asteroid('large', x, y, self.gm.speed_mul)
        self._asts.add(a); self._sprites.add(a)

    def _spawn_children(self, ast: Asteroid):
        for child in ast.split(self.gm.speed_mul):
            self._asts.add(child); self._sprites.add(child)

    def _spawn_powerup(self):
        weapon = random.choice(WEAPON_NAMES)
        for _ in range(20):
            x = random.uniform(60, WIDTH-60)
            y = random.uniform(60, HEIGHT-60)
            if self._player and math.hypot(x-self._player.x, y-self._player.y) > 160:
                break
        pu = PowerUp(weapon, x, y)
        self._powerups.add(pu); self._sprites.add(pu)

    # ─── eventos ──────────────────────────────────────────────────────────────
    def _events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                k = ev.key
                if k == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if   self.gm.state == MENU      and k == pygame.K_SPACE: self._new_game()
                elif self.gm.state == PLAYING   and k == pygame.K_p:     self.gm.state = PAUSED
                elif self.gm.state == PAUSED    and k == pygame.K_p:     self.gm.state = PLAYING
                elif self.gm.state == GAME_OVER and k == pygame.K_SPACE: self.gm.state = MENU

    # ─── laser contínuo ───────────────────────────────────────────────────────
    def _update_laser(self, dt: float):
        """Raycast frame-a-frame; danifica o primeiro asteroide na linha de visão."""
        self.snd.play_laser_hum()
        self._laser_active = True

        # Origem: nariz da nave
        ox, oy = ang_vec(self._player.angle, Player.NOSE + 3)
        rpx, rpy = self._player.x + ox, self._player.y + oy
        dx, dy   = ang_vec(self._player.angle)

        # Distância até a borda da tela
        edge_t = 1400.0
        if abs(dx) > 1e-6:
            tx = ((WIDTH if dx > 0 else 0) - rpx) / dx
            if tx > 0: edge_t = min(edge_t, tx)
        if abs(dy) > 1e-6:
            ty = ((HEIGHT if dy > 0 else 0) - rpy) / dy
            if ty > 0: edge_t = min(edge_t, ty)

        # Asteroide mais próximo no raio
        hit_t   = edge_t
        hit_ast = None
        for ast in self._asts:
            ok, t = ray_circle(rpx, rpy, dx, dy, ast.x, ast.y, ast.radius)
            if ok and 0 < t < hit_t:
                hit_t = t; hit_ast = ast

        # Caçador no raio (tem prioridade se mais próximo)
        hit_hunter = False
        if self._hunter:
            ok_h, t_h = ray_circle(rpx, rpy, dx, dy,
                                   self._hunter.x, self._hunter.y, HunterShip.radius)
            if ok_h and 0 < t_h < hit_t:
                hit_t = t_h; hit_ast = None; hit_hunter = True

        self._laser_end = (rpx + dx*hit_t, rpy + dy*hit_t)

        if self._laser_cd > 0: self._laser_cd -= dt

        if hit_hunter and self._laser_cd <= 0 and self._hunter:
            self._laser_cd = LASER_DAMAGE_CD
            pts = self._hunter.pts
            explode(self._parts, self._hunter.x, self._hunter.y, 16, RED)
            self.snd.play_explosion('large')
            got_life, got_bonus = self.gm.add_score(pts)
            if got_life:    self._set_flash("♥  VIDA EXTRA!", YELLOW)
            elif got_bonus: self._set_flash(f"+{GameManager.STREAK_PTS}  BÔNUS!", ORANGE)
            else:           self._set_flash(f"+{pts}  CAÇADOR ABATIDO!", RED)
            self._hunter = None

        if hit_ast and self._laser_cd <= 0:
            self._laser_cd = LASER_DAMAGE_CD
            col = CYAN if hit_ast.size != 'small' else WHITE
            explode(self._parts, hit_ast.x, hit_ast.y, 8, col)
            self.snd.play_explosion(hit_ast.size)
            got_life, got_bonus = self.gm.add_score(hit_ast.pts_value)
            if got_life:   self._set_flash("♥  VIDA EXTRA!", YELLOW)
            elif got_bonus: self._set_flash(f"+{GameManager.STREAK_PTS}  BÔNUS!", ORANGE)
            self._spawn_children(hit_ast); hit_ast.kill()

        # Faíscas ao longo do feixe
        if random.random() < 0.65:
            t_spark = random.uniform(0, hit_t * 0.95)
            self._parts.append(Particle(
                rpx + dx*t_spark, rpy + dy*t_spark, WEAPON_COLOR['LASER']))

    # ─── explosão de bomba ────────────────────────────────────────────────────
    def _detonate_bomb(self, ex: float, ey: float, destroyed: set):
        """Destrói todos os asteroides dentro do raio de explosão da bomba."""
        self._bomb_waves.append(BombExplosion(ex, ey))
        explode(self._parts, ex, ey, 40, WEAPON_COLOR['BOMBA'])
        self.snd.play_bomb()
        for ast in list(self._asts):
            if id(ast) in destroyed: continue
            if math.hypot(ast.x-ex, ast.y-ey) <= BombBullet.EXPLOSION_RADIUS:
                destroyed.add(id(ast))
                explode(self._parts, ast.x, ast.y, 12, ORANGE)
                self.snd.play_explosion(ast.size)
                got_life, _ = self.gm.add_score(ast.pts_value)
                if got_life: self._set_flash("♥  VIDA EXTRA!", YELLOW)
                self._spawn_children(ast); ast.kill()

    # ─── atualização ──────────────────────────────────────────────────────────
    def _update(self, keys, dt: float):
        self.gm.tick()
        if self._flash_t > 0: self._flash_t -= dt

        # Detecção de level-up → aviso e spawn de caçador
        cur_level = self.gm.level
        if cur_level > self._prev_level:
            self._prev_level = cur_level
            if self._hunter is None and self._hunter_warn <= 0:
                self._hunter_warn = HUNTER_WARN_DELAY
                self.snd.play_hunter_alert()

        if self._hunter_warn > 0:
            self._hunter_warn -= dt
            if self._hunter_warn <= 0:
                self._hunter_warn = 0.0
                self.snd.stop_hunter_alert()
                self._hunter = HunterShip(cur_level)

        self._player.update(keys, dt)

        # propulsor
        if self._player.thrusting: self.snd.play_thruster()
        else:                       self.snd.stop_thruster()

        # laser contínuo ou armas com projéteis
        if self._player.weapon == 'LASER' and keys[pygame.K_SPACE]:
            self._update_laser(dt)
        else:
            if self._laser_active:
                self._laser_active = False
                self._laser_end    = None
                self.snd.stop_laser_hum()

            max_b = WEAPON_MAX_BULLETS[self._player.weapon]
            if keys[pygame.K_SPACE] and len(self._bullets) < max_b:
                bullets = self._player.try_shoot()
                if bullets:
                    self.snd.play_shoot()
                    for b in bullets:
                        self._bullets.add(b); self._sprites.add(b)

        self._asts.update()
        self._bullets.update()
        self._powerups.update(dt)
        self._parts      = [p for p in self._parts      if p.update()]
        self._bomb_waves = [w for w in self._bomb_waves if w.update(dt)]

        # spawn asteroides
        if self.gm.should_spawn(dt, len(self._asts)): self._spawn_ast()

        # spawn power-ups
        if len(self._powerups) < self._PU_MAX_ON_SCREEN:
            self._pu_timer -= dt
            if self._pu_timer <= 0:
                self._spawn_powerup()
                self._pu_timer = random.uniform(self._PU_SPAWN_MIN, self._PU_SPAWN_MAX)

        # colisão projétil × asteroide
        destroyed: set = set()
        hits = pygame.sprite.groupcollide(
            self._bullets, self._asts, True, False, pygame.sprite.collide_circle)
        for bullet, ast_list in hits.items():
            for ast in ast_list:
                if id(ast) in destroyed: continue
                destroyed.add(id(ast))
                col = CYAN if ast.size != 'small' else WHITE
                explode(self._parts, ast.x, ast.y, 14, col)
                self.snd.play_explosion(ast.size)
                got_life, got_bonus = self.gm.add_score(ast.pts_value)
                if got_life:    self._set_flash("♥  VIDA EXTRA!", YELLOW)
                elif got_bonus: self._set_flash(f"+{GameManager.STREAK_PTS}  BÔNUS!", ORANGE)
                self._spawn_children(ast)
                # Bomba: explosão em área
                if isinstance(bullet, BombBullet):
                    self._detonate_bomb(ast.x, ast.y, destroyed)
                ast.kill()

        # colisão jogador × power-up
        for pu in list(self._powerups):
            if math.hypot(self._player.x-pu.x, self._player.y-pu.y) <= (Player.radius+pu.radius):
                self._player.collect_weapon(pu.weapon)
                self.snd.play_powerup()
                explode(self._parts, pu.x, pu.y, 10, WEAPON_COLOR[pu.weapon])
                self._set_flash(f"◆  {pu.weapon}!", WEAPON_COLOR[pu.weapon], 2.5)
                pu.kill()

        # colisão jogador × asteroide
        if not self._player.is_invincible:
            hit = pygame.sprite.spritecollideany(
                self._player, self._asts, pygame.sprite.collide_circle)
            if hit:
                explode(self._parts, self._player.x, self._player.y, 22, YELLOW)
                self.snd.play_death(); self.snd.stop_thruster(); self.snd.stop_laser_hum()
                self._laser_active = False
                if not self.gm.lose_life():
                    self._player.respawn()
                    self._set_flash("VIDA PERDIDA!", RED, 1.5)

        # atualizar caçador
        if self._hunter:
            alive = self._hunter.update(
                self._player.x, self._player.y, dt, self._parts)
            if not alive:
                self._hunter = None
            else:
                # colisão projéteis × caçador
                for b in list(self._bullets):
                    if math.hypot(b.x - self._hunter.x,
                                  b.y - self._hunter.y) <= (b.radius + HunterShip.radius):
                        pts = self._hunter.pts
                        explode(self._parts, self._hunter.x, self._hunter.y, 28, RED)
                        self.snd.play_explosion('large')
                        got_life, got_bonus = self.gm.add_score(pts)
                        if got_life:    self._set_flash("♥  VIDA EXTRA!", YELLOW)
                        elif got_bonus: self._set_flash(f"+{GameManager.STREAK_PTS}  BÔNUS!", ORANGE)
                        else:           self._set_flash(f"+{pts}  CAÇADOR ABATIDO!", RED)
                        b.kill()
                        self._hunter = None
                        break

                # colisão jogador × caçador
                if (self._hunter and not self._player.is_invincible and
                        math.hypot(self._player.x - self._hunter.x,
                                   self._player.y - self._hunter.y)
                        <= (Player.radius + HunterShip.radius)):
                    explode(self._parts, self._player.x, self._player.y, 22, YELLOW)
                    self.snd.play_death()
                    self.snd.stop_thruster(); self.snd.stop_laser_hum()
                    self._laser_active = False
                    self._hunter = None
                    if not self.gm.lose_life():
                        self._player.respawn()
                        self._set_flash("CAÇADOR TE PEGOU!", RED, 1.5)

    def _set_flash(self, msg, col=WHITE, dur=2.0):
        self._flash_msg = msg; self._flash_col = col; self._flash_t = dur

    # ─── HUD ──────────────────────────────────────────────────────────────────
    def _draw_hud(self):
        heart = self.f_sm.render("♥", True, RED)
        for i in range(self.gm.lives):
            self.screen.blit(heart, (10+i*24, 10))

        sc = self.f_md.render(f"{self.gm.score:08d}", True, YELLOW)
        self.screen.blit(sc, (WIDTH-sc.get_width()-10, 8))

        if self.gm.streak > 0:
            st = self.f_sm.render(f"COMBO ×{self.gm.streak}", True, ORANGE)
            self.screen.blit(st, (WIDTH//2-st.get_width()//2, 10))

        lv = self.f_xs.render(f"LVL {self.gm.level}", True, GRAY)
        self.screen.blit(lv, (WIDTH//2-lv.get_width()//2, 34))

        if self._player and self._player.weapon != 'NORMAL':
            self._draw_weapon_hud()

        # aviso de caçador se aproximando
        if self._hunter_warn > 0 and int(self._hunter_warn * 5) % 2 == 0:
            self._ctext(self.screen, "⚠  CAÇADOR SE APROXIMA!", self.f_md, RED, HEIGHT//2 - 30)

        # indicador de caçador ativo (canto inferior esquerdo)
        if self._hunter:
            ind = self.f_xs.render("▲ CAÇADOR", True, RED)
            if int(time.time() * 3) % 2 == 0:
                self.screen.blit(ind, (10, HEIGHT - 24))

        if self._flash_t > 0:
            a = min(1.0, self._flash_t)
            col = tuple(int(c*a) for c in self._flash_col)
            self._ctext(self.screen, self._flash_msg, self.f_md, col, HEIGHT//2-60)

    def _draw_weapon_hud(self):
        p   = self._player
        col = WEAPON_COLOR[p.weapon]
        ratio = p.weapon_timer / WEAPON_DURATION

        bar_w, bar_h = 240, 10
        bar_x = WIDTH//2 - bar_w//2
        bar_y = HEIGHT - 36

        lbl = self.f_sm.render(f"◆ {p.weapon}", True, col)
        self.screen.blit(lbl, (WIDTH//2-lbl.get_width()//2, bar_y-22))

        secs = self.f_xs.render(f"{int(p.weapon_timer)}s", True, col)
        self.screen.blit(secs, (bar_x+bar_w+6, bar_y))

        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, bar_w, bar_h), 1)
        if p.weapon_timer > 10 or int(p.weapon_timer*4)%2 == 0:
            fill_w = int(bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(self.screen, col, (bar_x, bar_y, fill_w, bar_h))

    # ─── renderização ─────────────────────────────────────────────────────────
    def _bg(self):
        t = min(self.gm.score/30_000, 1.0)
        return int(t*12), int(t*7), int(18+t*18)

    def _ctext(self, surf, txt, font, col, y, cx=WIDTH//2):
        s = font.render(txt, True, col)
        surf.blit(s, (cx-s.get_width()//2, y))

    def _draw_laser_beam(self):
        if not self._laser_active or not self._laser_end:
            return
        p1 = (int(self._player.x), int(self._player.y))
        p2 = (int(self._laser_end[0]), int(self._laser_end[1]))
        col = WEAPON_COLOR['LASER']      # (220, 30, 30)
        dim = tuple(c//4 for c in col)
        mid = tuple(c//2 for c in col)
        pygame.draw.line(self.screen, dim, p1, p2, 9)
        pygame.draw.line(self.screen, mid, p1, p2, 5)
        pygame.draw.line(self.screen, col, p1, p2, 2)
        pygame.draw.line(self.screen, WHITE, p1, p2, 1)

    def _draw_playing(self):
        self.screen.fill(self._bg())
        self.stars.draw(self.screen)
        self._sprites.draw(self.screen)
        if self._hunter:
            self._hunter.draw(self.screen)
        self._draw_laser_beam()
        for w in self._bomb_waves: w.draw(self.screen)
        for p in self._parts:      p.draw(self.screen)
        self._draw_hud()

    def _draw_menu(self):
        self.screen.fill(DARK_BG)
        self.stars.draw(self.screen)
        self._menu_asts.update(); self._menu_asts.draw(self.screen)
        self._ctext(self.screen, GAME_NAME, self.f_lg, YELLOW, 100)
        if int(time.time()*2) % 2 == 0:
            self._ctext(self.screen, "PRESSIONE  ESPAÇO  PARA  COMEÇAR", self.f_md, WHITE, 190)

        controls = [("← →","Rotacionar"),("↑","Acelerar"),
                    ("ESPAÇO","Atirar"),("P","Pausar"),("ESC","Sair")]
        y = 265
        for key, act in controls:
            self.screen.blit(self.f_sm.render(f"  {key:<10}  {act}", True, GRAY),
                             (WIDTH//2-145, y))
            y += 28

        self._ctext(self.screen, "── POWER-UPS ──", self.f_xs, GRAY, y+12)
        y += 34
        shorts = {'BOMBA':'BM','TRIPLO':'D3','LASER':'LS','ESPALHADO':'S5','TRASEIRO':'TR'}
        for wname in WEAPON_NAMES:
            col  = WEAPON_COLOR[wname]
            tag  = self.f_xs.render(f"[{shorts[wname]}]", True, col)
            desc = self.f_xs.render(WEAPON_DESC[wname], True, GRAY)
            self.screen.blit(tag,  (WIDTH//2-145, y))
            self.screen.blit(desc, (WIDTH//2-105, y))
            y += 22

    def _draw_paused(self):
        self._draw_playing()
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,150)); self.screen.blit(ov, (0,0))
        self._ctext(self.screen, "PAUSADO", self.f_lg, YELLOW, HEIGHT//2-40)
        self._ctext(self.screen, "Pressione  P  para continuar", self.f_sm, WHITE, HEIGHT//2+30)

    def _draw_gameover(self):
        self.screen.fill(BLACK); self.stars.draw(self.screen)
        self._ctext(self.screen, "GAME  OVER", self.f_lg, RED, 90)
        self._ctext(self.screen, f"{self.gm.score:08d}", self.f_lg, YELLOW, 170)
        self._ctext(self.screen, f"LEVEL  {self.gm.level}  ALCANÇADO", self.f_md, WHITE, 258)
        m, s = divmod(int(self.gm.elapsed), 60)
        self._ctext(self.screen, f"TEMPO  {m:02d}:{s:02d}", self.f_md, GRAY, 305)
        if int(time.time()*2) % 2 == 0:
            self._ctext(self.screen, "ESPAÇO  →  MENU", self.f_sm, WHITE, 400)

    # ─── loop principal ────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt   = self.clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()
            self._events()

            st = self.gm.state
            if   st == MENU:      self._draw_menu()
            elif st == PLAYING:   self._update(keys, dt); self._draw_playing()
            elif st == PAUSED:    self._draw_paused()
            elif st == GAME_OVER: self._draw_gameover()

            pygame.display.flip()
